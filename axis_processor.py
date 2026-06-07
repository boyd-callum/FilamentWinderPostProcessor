from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd



@dataclass
class AxisProcessorConfig:

    x_clearance_mm: float = 10.0
    z_clearance_mm: float = 50.0
    default_feedrate_mm_min: float = 500.0
    default_tension_n: float = 20.0

    x_column: str = "x_mm"
    y_column: str = "y_mm"
    z_column: str = "z_mm"

    output_spindle_column: str = "A_deg"
    output_z_column: str = "Z_mm"
    output_x_column: str = "X_mm"
    output_head_column: str = "B_deg"
    output_feedrate_column: str = "F_mm_min"
    output_tension_column: str = "tension_N"



class AxisProcessor:

    def __init__(self, config: AxisProcessorConfig) -> None:
        self.config = config

    

    def process_csv(
            self,
            input_path_csv: str | Path,
            output_axis_csv: str | Path
    ) -> None:
        
        path_table = pd.read_csv(input_path_csv)
        

        # process the dataframe

        self._validate_path_table(path_table)

        x = path_table[self.config.x_column].to_numpy(dtype=float)
        y = path_table[self.config.y_column].to_numpy(dtype=float)
        z = path_table[self.config.z_column].to_numpy(dtype=float)

        radius = np.sqrt(x**2 + y**2)

        # need to unwrap so that A-axis doesnt jump from 360 deg back to 0
        theta_rad = np.unwrap(np.arctan2(y, x))
        spindle_deg = np.degrees(theta_rad)

        x_axis_mm = radius + self.config.x_clearance_mm
        z_axis_mm = z + self.config.z_clearance_mm

        head_deg = self._calculate_head_angle_deg(x, y, z)

        axis_table = pd.DataFrame(
            {
                self.config.output_spindle_column: spindle_deg,
                self.config.output_z_column: z_axis_mm,
                self.config.output_x_column: x_axis_mm,
                self.config.output_head_column: head_deg,
                self.config.output_feedrate_column: self.config.default_feedrate_mm_min,
                self.config.output_tension_column: self.config.default_tension_n,
            }
        )


        axis_table.to_csv(output_axis_csv, index=False)
        
    

    
    def _validate_path_table(self, path_table: pd.DataFrame) -> None:

        required_columns = [
            self.config.x_column,
            self.config.y_column,
            self.config.z_column
        ]
    
        missing_columns = [
            column for column in required_columns
            if column not in path_table.columns
        ]

        if missing_columns:
            raise ValueError(
                "Path table is missing required columns: "+", ".join(missing_columns)
            )
        
    
    def _calculate_head_angle_deg(
            self,
            x: np.ndarray,
            y: np.ndarray,
            z: np.ndarray,
    ) -> np.ndarray:
        """
        Calculate the required payout-head rotation angle from the fibre path.

        Assumes:
            - spindle axis is aligned with +Z
            - fibre path points lie on the laminate surface
            - head rotation is measured relative to the mandrel axis

        Returns:
            Head rotation angle in degrees.
            0 deg corresponds to axial winding.
            ±90 deg corresponds to hoop winding.
        """

        # each row is a point on the fibre trajectory
        points = np.column_stack((x, y, z))

        # estimate the local fibre direction at each point
        tangents = np.gradient(points, axis = 0)

        # normalise tangents so we can use dot products properly
        tangent_norms = np.linalg.norm(tangents, axis = 1)
        tangent_norms[tangent_norms == 0] = 1.0
        tangents = tangents / tangent_norms[: , None]

        # calculate distance from madrel centreline at each point
        radius = np.sqrt(x**2 + y**2)
        radius[radius == 0] = 1.0


        # cylindrical coordinates basis vectors:
        # radial:
        #     points away from the mandrel centreline
        #
        # circumferential:
        #     tangent to a circle of constant radius
        #     (direction of positive spindle rotation)
        #
        # axial:
        #     direction along the mandrel centreline (+Z)

        radial = np.column_stack(
            ( x/radius, y/radius, np.zeros_like(x) )
        )
        circumferential = np.column_stack(
            ( -y/radius, x/radius, np.zeros_like(x) )
        )
        axial = np.tile(
            np.array( [0.0, 0.0, 1.0] ), 
            (len(x), 1)
        )

        # resolve the fibre tangent into circumferential and axial components
        tangential_component = np.sum(tangents * circumferential, axis = 1)
        axial_component = np.sum(tangents * axial, axis = 1)

        # angle of fibre direction relative to z axis
        # 0 deg - purely axial
        # 90 deg - purely circumferential / hoop winding
        head_deg = np.degrees(
            np.arctan2( tangential_component, axial_component )
        )

        return head_deg