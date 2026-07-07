# generate_example_fibre_path.py

from pathlib import Path

import numpy as np
import pandas as pd


def generate_multilayer_cylinder_path(
    output_path: str | Path = "fibre_path.csv",
    radius_mm: float = 40.0,
    cylinder_length_mm: float = 155.0,
    number_of_layers: int = 4,
    layer_thickness_mm: float = 0.3,
    points_per_layer: int = 32,
    revolutions_per_layer: float = 1.0,
) -> None:
    rows = []

    z = np.linspace(0.0, cylinder_length_mm, points_per_layer)

    for layer in range(number_of_layers):
        # Increase radius for each layer to simulate laminate build-up.
        layer_radius = radius_mm + layer * layer_thickness_mm

        # Reverse winding direction on alternating layers.
        direction = 1 if layer % 2 == 0 else -1

        theta = direction * np.linspace(
            0.0,
            2.0 * np.pi * revolutions_per_layer,
            points_per_layer,
        )

        # Add a small phase offset per layer so layers are not exactly stacked.
        theta += layer * np.deg2rad(10.0)

        x = layer_radius * np.cos(theta)
        y = layer_radius * np.sin(theta)

        for i in range(points_per_layer):
            rows.append(
                {
                    "x_mm": x[i],
                    "y_mm": y[i],
                    "z_mm": z[i],
                    "layer": layer,
                }
            )

    fibre_path = pd.DataFrame(rows)

    fibre_path.to_csv(
        output_path,
        index=False,
        float_format="%.3f",
    )


if __name__ == "__main__":
    generate_multilayer_cylinder_path(
        output_path="fibre_path.csv",
        radius_mm=40.0,
        cylinder_length_mm=155.0,
        number_of_layers=4,
        layer_thickness_mm=0.3,
        points_per_layer=32,
        revolutions_per_layer=1.0,
    )