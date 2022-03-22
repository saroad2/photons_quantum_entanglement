import json
from pathlib import Path

import click
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from scipy import optimize


def trim_data(x, y):
    x_min, x_max = x.min(), x.max()
    x_std = (x_max - x_min) / np.sqrt(12)
    y_mean, y_std = y.mean(), y.std()
    x_of_big_ys = x[np.fabs(y - y_mean) > y_std]
    x_trim_start, x_trim_end = x_of_big_ys.min() - x_std / 2, x_of_big_ys.max() + x_std / 2
    indices = (x_trim_start < x) & (x < x_trim_end)
    x, y = x[indices], y[indices]
    return x[y != 0], y[y != 0]


def wave_packet(x, I, f, sigma, phi):
    return I / 2 * (1 + np.exp(-(np.pi * f * x) ** 2 / (4 * np.log(2))) * np.cos(2 * np.pi * sigma * x + phi))


@click.command()
@click.argument("csv_path", type=click.Path(exists=True, dir_okay=False))
@click.option("-c", "--column", type=str, required=True)
@click.option(
    "-o", "--output-dir", type=click.Path(file_okay=False), required=True
)
def mi_fit(csv_path, column, output_dir):
    csv_path = Path(csv_path)
    output_dir = Path(output_dir)
    df = pd.read_csv(csv_path)
    x = df["x"].to_numpy()
    y = df[column].to_numpy()
    x, y = trim_data(x, y)

    p0 = [1, 1, 20, 1]
    x0 = x[y.argmax()]
    y_max = y.max()
    sigma = np.sqrt(y) / y_max
    popt, pcov = optimize.curve_fit(
        wave_packet,
        xdata=x - x0,
        ydata=y / y_max,
        p0=p0,
        sigma=sigma
    )
    errors = np.sqrt(np.diagonal(pcov))
    print(popt)
    print(pcov)
    residuals = y / y_max - wave_packet(x - x0, *popt)
    chi2 = np.sum((residuals / sigma) ** 2)
    print(f"{chi2=}")

    # Results json
    with open(output_dir / f"{csv_path.stem}_{column.replace(' ', '_')}_res.json", mode="w") as fd:
        json.dump(
            dict(
                result=popt.tolist(),
                covariance=pcov.tolist(),
                errors=errors.tolist(),
                percentage_errors=(errors / np.fabs(popt) * 100).tolist(),
                chi2=chi2
            ),
            fd,
            indent=2
        )

    # Plot
    plt.title("Michelson interferometer")
    plt.xlabel("Wedge position [mm]")
    plt.ylabel("Coincidence rate")
    plt.scatter(x, y)
    plt.plot(x, wave_packet(x - x0, *popt) * y_max)
    plt.savefig(output_dir / f"{csv_path.stem}_{column.replace(' ', '_')}_fit")
    plt.clf()


if __name__ == '__main__':
    mi_fit()
