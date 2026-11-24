#!/usr/bin/env python3

import argparse
import json
import re
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


def read_cube_volume(block_mesh_path):
    content = block_mesh_path.read_text()

    match = re.search(
        r"\bvertices\s*\((.*?)\)\s*;",
        content,
        flags=re.DOTALL
    )

    if not match:
        raise ValueError(f"Cannot find vertices in {block_mesh_path}")

    vertices = re.findall(
        r"\(\s*([-+0-9.eE]+)\s+"
        r"([-+0-9.eE]+)\s+"
        r"([-+0-9.eE]+)\s*\)",
        match.group(1)
    )

    if not vertices:
        raise ValueError(f"No vertices found in {block_mesh_path}")

    points = [
        tuple(map(float, vertex))
        for vertex in vertices
    ]

    dimensions = [
        max(point[axis] for point in points)
        - min(point[axis] for point in points)
        for axis in range(3)
    ]

    volume = dimensions[0] * dimensions[1] * dimensions[2]

    if volume <= 0:
        raise ValueError("Calculated cube volume must be positive")

    return volume, dimensions


def main():
    parser = argparse.ArgumentParser(
        description="Plot OpenFOAM temperature and analytical solution."
    )

    parser.add_argument(
        "--csv",
        type=Path,
        default=Path("results/temperature.csv")
    )
    parser.add_argument(
        "--material",
        type=Path,
        default=Path("FIP-1.0/material/steel_1045_v1.json")
    )
    parser.add_argument(
        "--regime",
        type=Path,
        default=Path("FIP-1.0/regimes/REG-01.json")
    )
    parser.add_argument(
        "--block-mesh",
        type=Path,
        default=Path("cases/00_adiabatic_cube/system/blockMeshDict")
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("results/T_vs_time.png")
    )

    args = parser.parse_args()

    for path in (
        args.csv,
        args.material,
        args.regime,
        args.block_mesh
    ):
        if not path.is_file():
            parser.error(f"File not found: {path}")

    df = pd.read_csv(args.csv)

    required_columns = {"time_s", "T_min_K"}
    if not required_columns.issubset(df.columns):
        parser.error(
            f"CSV must contain columns: {sorted(required_columns)}"
        )

    with args.material.open() as file:
        material = json.load(file)

    with args.regime.open() as file:
        regime = json.load(file)

    rho_cp = material["solid"]["level_A_constant"]["rho_cp_J_m3K"]
    power = regime["laser"]["power_W"]
    absorptivity = regime["laser"]["absorptivity"]
    initial_temperature = regime["thermal"]["preheat_K"]

    volume, dimensions = read_cube_volume(args.block_mesh)

    absorbed_power = power * absorptivity
    slope = absorbed_power / (rho_cp * volume)

    time = df["time_s"].to_numpy()
    numerical_temperature = df["T_min_K"].to_numpy()

    analytical_temperature = initial_temperature + slope * time
    deviation = numerical_temperature - analytical_temperature

    fig, (ax_temperature, ax_deviation) = plt.subplots(
        2,
        1,
        figsize=(10, 8),
        sharex=True,
        gridspec_kw={"height_ratios": [2, 1]}
    )

    ax_temperature.plot(
        time,
        numerical_temperature,
        "o-",
        label="Расчёт OpenFOAM"
    )
    ax_temperature.plot(
        time,
        analytical_temperature,
        "--",
        label="Аналитическое решение"
    )

    ax_temperature.set_ylabel("Температура, K")
    ax_temperature.set_title(
        "Кейс 00: нагрев адиабатного куба"
    )
    ax_temperature.grid(True)
    ax_temperature.legend()

    ax_deviation.plot(
        time,
        deviation,
        "o-",
        label="OpenFOAM − аналитическое решение"
    )
    ax_deviation.axhline(0, linestyle="--")
    ax_deviation.set_xlabel("Время, с")
    ax_deviation.set_ylabel("Отклонение, K")
    ax_deviation.grid(True)
    ax_deviation.legend()

    fig.tight_layout()

    args.output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(args.output, dpi=300, bbox_inches="tight")
    plt.close(fig)

    print(f"CSV: {args.csv}")
    print(f"Material: {args.material}")
    print(f"Regime: {args.regime}")
    print(f"Cube dimensions: {dimensions} m")
    print(f"Cube volume: {volume:.9e} m^3")
    print(f"Absorbed power: {absorbed_power:.6f} W")
    print(f"Volumetric heat capacity: {rho_cp:.6e} J/(m^3 K)")
    print(f"Analytical slope: {slope:.9f} K/s")
    print(f"Initial temperature: {initial_temperature:.6f} K")
    print(f"Maximum absolute deviation: {abs(deviation).max():.12e} K")
    print(f"Plot: {args.output}")


if __name__ == "__main__":
    main()
