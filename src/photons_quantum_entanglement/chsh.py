import click
import pandas as pd
from uncertainties import ufloat

ALPHA_PERP_DICT = {
    "H": "V",
    "V": "H",
    "+": "-",
    "-": "+",
}
VALUE_COLUMN = "Mean Correlation"
ERROR_COLUMN = "total deviation"


def alpha_perp(alpha):
    return ALPHA_PERP_DICT[alpha]


def beta_perp(beta):
    return beta + 90


def C_value(df, alpha, beta):
    values = df.loc[(df["alpha"] == alpha) & (df["beta"] == beta)]
    if values.shape[0] != 1:
        raise ValueError(f"Couldn't find {alpha=}, {beta=}")
    row = values.iloc[0]
    return ufloat(row[VALUE_COLUMN], row[ERROR_COLUMN])


def E_value(df, alpha, beta):
    c_alpha_beta = C_value(df, alpha, beta)
    c_alpha_perp_beta = C_value(df, alpha_perp(alpha), beta)
    c_alpha_beta_perp = C_value(df, alpha, beta_perp(beta))
    c_alpha_perp_beta_perp = C_value(df, alpha_perp(alpha), beta_perp(beta))
    return (
        c_alpha_beta + c_alpha_perp_beta_perp - c_alpha_perp_beta - c_alpha_beta_perp
    ) / (c_alpha_beta + c_alpha_perp_beta_perp + c_alpha_perp_beta + c_alpha_beta_perp)


@click.command()
@click.option(
    "-x", "--excel-path", type=click.Path(exists=True, dir_okay=False), required=True
)
@click.option("-s", "--sheet-name", type=str, required=True)
def chsh_calc(excel_path, sheet_name):
    df = pd.read_excel(excel_path, sheet_name=sheet_name)
    e_H_22 = E_value(df, "H", 22.5)
    e_plus_22 = E_value(df, "+", 22.5)
    e_H_67 = E_value(df, "H", 67.5)
    e_plus_67 = E_value(df, "+", 67.5)
    chsh = e_H_22 + e_plus_22 - e_H_67 + e_plus_67
    n_delta = (chsh.nominal_value - 2) / chsh.std_dev
    print(f"{e_H_22=} ({e_H_22.std_dev / e_H_22.nominal_value * 100:.2f}%)")
    print(f"{e_H_67=} ({e_H_67.std_dev / e_H_67.nominal_value * 100:.2f}%)")
    print(f"{e_plus_22=} ({e_plus_22.std_dev / e_plus_22.nominal_value * 100:.2f}%)")
    print(f"{e_plus_67=} ({e_plus_67.std_dev / e_plus_67.nominal_value * 100:.2f}%)")
    print(f"{chsh=}")
    print(f"{n_delta=}")


if __name__ == "__main__":
    chsh_calc()
