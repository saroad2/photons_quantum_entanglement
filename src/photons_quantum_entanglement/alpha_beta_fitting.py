import json
from pathlib import Path

import click
import click_params as clickp
import pandas as pd
import numpy as np
from scipy.optimize import curve_fit
from matplotlib import pyplot as plt


def malus(x, a, b, c, d):
    return a / 2 * (1 - b * np.sin((x - d) / c))


@click.command()
@click.option(
    "-x", "--excel-path", type=click.Path(exists=True, dir_okay=False), required=True
)
@click.option("-s", "--sheet-name", type=str, required=True)
@click.option("-a", "--alpha", type=clickp.IntListParamType(), default="0,45,90,135")
@click.option("-b", "--betac", type=clickp.FloatListParamType(), default="3,3,3,3")
@click.option("-o", "--output-dir", type=click.Path(file_okay=False), required=True)
def fit_alpha_beta(excel_path, alpha, betac, output_dir, sheet_name):
    output_dir = Path(output_dir)
    df = pd.read_excel(excel_path, sheet_name=sheet_name)

    for alpha_value, betac_value in zip(alpha, betac):
        click.echo(f"Fitting alpha={alpha_value}")
        data_column = f"alpha={alpha_value}"

        df["beta radians"] = df["beta"] / 180 * np.pi
        max_column = float(df[data_column].max())

        x = df["beta radians"].to_numpy()
        y = df[data_column].to_numpy() / max_column
        sigma = np.sqrt(df[data_column].to_numpy()) / max_column
        p0 = [1, 1, np.pi / 4, betac_value]
        popt, pcov = curve_fit(
            malus,
            xdata=x,
            ydata=y,
            p0=p0,
            sigma=sigma,
            bounds=(0, 6 * np.pi),
            absolute_sigma=True,
        )

        errors = np.sqrt(np.diagonal(pcov))
        fitted_values = malus(x, *popt)
        residuals = y - fitted_values
        chi2 = np.sum((residuals / sigma) ** 2)
        output_dir.mkdir(exist_ok=True, parents=True)

        # Results json
        with open(
            output_dir / f"alpha_beta_fit_{alpha_value}_results.json", mode="w"
        ) as fd:
            json.dump(
                dict(
                    result=popt.tolist(),
                    max_value=max_column,
                    covariance=pcov.tolist(),
                    errors=errors.tolist(),
                    percentage_errors=(errors / popt * 100).tolist(),
                    chi2=chi2,
                ),
                fd,
                indent=2,
            )

        # Plot
        plt.title(rf"Coincidence rate by angle, $\alpha={alpha_value}$")
        plt.xlabel(rf"$\beta$ [degrees]")
        plt.ylabel("Coincidence count")
        plt.plot(df["beta"], fitted_values * max_column)
        plt.errorbar(
            df["beta"],
            df[data_column],
            yerr=sigma * max_column,
            linestyle="none",
            marker=".",
            markersize=5,
        )
        plt.savefig(output_dir / f"alpha_beta_fit_{alpha_value}")
        plt.clf()

        # Residuals Plot
        plt.title(
            rf"Coincidence rate by angle residuals, $\alpha={alpha_value}$. $\chi^2={chi2:.2f}$"
        )
        plt.xlabel(rf"$\beta$ [degrees]")
        plt.ylabel("Coincidence count error")
        plt.errorbar(
            df["beta"], np.zeros(shape=np.shape(x)), yerr=residuals * max_column
        )
        plt.savefig(output_dir / f"alpha_beta_fit_{alpha_value}_residuals")
        plt.clf()


if __name__ == "__main__":
    fit_alpha_beta()
