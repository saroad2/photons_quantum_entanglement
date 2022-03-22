from pathlib import Path

import click
import pandas as pd
from matplotlib import pyplot as plt


@click.command()
@click.argument("csv_path", type=click.Path(exists=True, dir_okay=False))
@click.option(
    "-o", "--output-dir", type=click.Path(file_okay=False), required=True
)
def hom_plot(csv_path, output_dir):
    csv_path = Path(csv_path)
    output_dir = Path(output_dir)
    df = pd.read_csv(csv_path)
    x = df["x"]
    y = df["coincidence 01"]
    plt.title("HOM interference")
    plt.xlabel("Position delta [mm]")
    plt.ylabel("Coincidence rate")
    plt.plot(x, y)
    plt.savefig(output_dir / f"{csv_path.stem}_plot")


if __name__ == '__main__':
    hom_plot()
