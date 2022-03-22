import csv
from pathlib import Path

import click


@click.command()
@click.argument("txt_path", type=click.Path(exists=True, dir_okay=False))
def convert_linear_scan_to_csv(txt_path):
    txt_path = Path(txt_path)
    with open(txt_path, mode="r") as fd:
        lines = fd.readlines()
    lines = [
        line.replace("\n", "")
        for line in lines
        if not line.startswith("=") and not line.startswith("#")
    ]
    splitted_lines = [
        line.split()[:6]
        for line in lines
    ]
    columns = ["x", "coincidence 0", "coincidence 1", "coincidence 2", "coincidence 3", "coincidence 01"]
    directory = txt_path.parent
    with open(directory / f"{txt_path.stem}.csv", mode="w", newline="") as fd:
        writer = csv.writer(fd)
        writer.writerow(columns)
        writer.writerows(splitted_lines)


if __name__ == '__main__':
    convert_linear_scan_to_csv()
