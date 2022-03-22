import json
from pathlib import Path

import click
import pandas as pd
from uncertainties import ufloat

DURATION_COLUMN = "duration in seconds"
CURRENT_COLUMN = "Current"
MEASUREMENT_NAME_COLUMN = "Measurement name"
VALUE_COLUMN = "Mean value"
ERROR_COLUMN = "total deviation"


def C_value(df, measurement_name):
    values = df.loc[(df[MEASUREMENT_NAME_COLUMN] == measurement_name)]
    if values.shape[0] != 1:
        raise ValueError(f"Couldn't find {measurement_name=}")
    row = values.iloc[0]
    return ufloat(row[VALUE_COLUMN], row[ERROR_COLUMN])


def calc_g2(df, current, duration):
    spec_df = df.loc[(df[CURRENT_COLUMN] == current) & (df[DURATION_COLUMN] == duration)]
    n1 = C_value(spec_df, "N1")
    n2 = C_value(spec_df, "N2")
    n12 = C_value(spec_df, "N12")
    return n12 / (n1 * n2 * duration)


def calc_gh2(df, current, duration):
    spec_df = df.loc[(df[CURRENT_COLUMN] == current) & (df[DURATION_COLUMN] == duration)]
    n0 = C_value(spec_df, "N0")
    n01 = C_value(spec_df, "N01")
    n02 = C_value(spec_df, "N02")
    n012 = C_value(spec_df, "N012")
    return (n0 * n012) / (n01 * n02)


@click.command()
@click.option(
    "-x", "--excel-path", type=click.Path(exists=True, dir_okay=False), required=True
)
@click.option(
    "-s", "--sheet-name", type=str, required=True
)
@click.option(
    "-o", "--output-dir", type=click.Path(file_okay=False), required=True
)
def g_calc(excel_path, sheet_name, output_dir):
    output_dir = Path(output_dir)
    df = pd.read_excel(excel_path, sheet_name=sheet_name)
    measurements = []
    for current in df[CURRENT_COLUMN].unique():
        for duration in df.loc[df[CURRENT_COLUMN] == current][DURATION_COLUMN].unique():
            print(f"{current=}, {duration=}")
            g2 = calc_g2(df, current=current, duration=duration)
            gh2 = calc_gh2(df, current=current, duration=duration)
            print(f"{g2=}, {gh2=}")
            measurements.append(
                dict(
                    current=current,
                    duration=duration,
                    g2=g2.nominal_value,
                    g2_error=g2.std_dev,
                    g2_percentage_error=g2.std_dev / g2.nominal_value * 100,
                    gh2=gh2.nominal_value,
                    gh2_error=gh2.std_dev,
                    gh2_percentage_error=gh2.std_dev / gh2.nominal_value * 100,
                )
            )

    output_dir.mkdir(exist_ok=True, parents=True)
    with open(output_dir / "hbt_measurements.json", mode="w") as fd:
        json.dump(dict(measurements=measurements), fd, indent=2)


if __name__ == '__main__':
    g_calc()
