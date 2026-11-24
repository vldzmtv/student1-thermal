#!/usr/bin/env python3

import argparse
import csv
import re
from pathlib import Path


def read_temperature_field(path):
    content = path.read_text()

    content = re.sub(r"/\*.*?\*/", "", content, flags=re.DOTALL)
    content = re.sub(r"//.*?$", "", content, flags=re.MULTILINE)

    uniform = re.search(
        r"\binternalField\s+uniform\s+([-+0-9.eE]+)\s*;",
        content
    )

    if uniform:
        value = float(uniform.group(1))
        return [value]

    nonuniform = re.search(
        r"\binternalField\s+nonuniform\s+List<scalar>\s+"
        r"(\d+)\s*\((.*?)\)\s*;",
        content,
        flags=re.DOTALL
    )

    if not nonuniform:
        raise ValueError(f"Unsupported internalField format: {path}")

    expected_count = int(nonuniform.group(1))
    values = [
        float(value)
        for value in re.findall(
            r"[-+]?(?:\d+\.?\d*|\.\d+)(?:[eE][-+]?\d+)?",
            nonuniform.group(2)
        )
    ]

    if len(values) != expected_count:
        raise ValueError(
            f"{path}: expected {expected_count} values, "
            f"got {len(values)}"
        )

    return values


def main():
    parser = argparse.ArgumentParser(
        description="Extract temperature statistics from OpenFOAM fields."
    )
    parser.add_argument("case", type=Path, help="Path to OpenFOAM case")
    parser.add_argument(
        "-o", "--output",
        type=Path,
        default=Path("results/temperature.csv"),
        help="Output CSV path (default: results/temperature.csv)"
    )
    args = parser.parse_args()

    case = args.case.resolve()

    if not case.is_dir():
        parser.error(f"Case directory does not exist: {case}")

    rows = []

    time_dirs = sorted(
        (
            path for path in case.iterdir()
            if path.is_dir() and re.fullmatch(
                r"\d+(?:\.\d*)?(?:[eE][-+]?\d+)?", path.name
            )
            and (path / "T").is_file()
        ),
        key=lambda path: float(path.name)
    )

    if not time_dirs:
        parser.error(f"No time directories containing T found in {case}")

    for time_dir in time_dirs:
        values = read_temperature_field(time_dir / "T")

        rows.append({
            "time_s": float(time_dir.name),
            "T_min_K": min(values),
            "T_max_K": max(values)
        })

    output = args.output.resolve()
    output.parent.mkdir(parents=True, exist_ok=True)

    with output.open("w", newline="") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=["time_s", "T_min_K", "T_max_K"]
        )
        writer.writeheader()
        writer.writerows(rows)

    print(f"Case: {case}")
    print(f"Time steps: {len(rows)}")
    print(f"CSV: {output}")
    print(f"Final T_min: {rows[-1]['T_min_K']:.8f} K")
    print(f"Final T_max: {rows[-1]['T_max_K']:.8f} K")


if __name__ == "__main__":
    main()
