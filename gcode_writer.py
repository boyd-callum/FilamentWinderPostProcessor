
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import pandas as pd


@dataclass
class GCodeWriterConfig:

    linear_units: str = "mm"
    positioning_mode: str = "absolute" # "absolute" or "relative"
    feedrate_mode: str = "units_per_min" # G94

    axis_precision: int = 3
    feedrate_precision: int = 1

    include_line_numbers: bool = False
    line_number_start: int = 0
    line_number_step: int = 1

    program_name: Optional[str] = "FILAMENT_WINDING_PATH"

    spindle_axis_name: str = "A"
    z_axis_name: str = "Z"
    x_axis_name: str = "X"
    head_axis_name: str = "B"

    spindle_column: str = "A_deg"
    z_column: str = "Z_mm"
    x_column: str = "X_mm"
    head_column: str = "B_deg"
    feedrate_column: str = "F_mm_min"
    tension_column: Optional[str] = "tension_N"

    output_tension_as_comment: bool = True



class GCodeWriter:

    def __init__(self, config: GCodeWriterConfig) -> None:
        
        self.config = config


    def _make_header(self) -> list[str]:

        
        lines = []

        # nice to put the program name at the top of the program
        if self.config.program_name is not None:
            lines.append(f"({self.config.program_name})")


        # set what linear units we are using (G20 or G21)
        if self.config.linear_units == "mm":
            lines.append("G21 (mm)")
        elif self.config.linear_units == "inch":
            lines.append("G20 (inch)")
        else:
            raise ValueError(f"unsupported linear units: {self.config.linear_units}")
        

        # absolute or relative positioning? (G90 or G91)
        if self.config.positioning_mode == "absolute":
            lines.append("G90 (absolute positioning)")
        elif self.config.positioning_mode == "relative":
            lines.append("G91 (relative positioning)")
        else:
            raise ValueError(f"Unsupported positioning mode: {self.config.positioning_mode}")


        # what feedrate units (G94 for units per min)
        # no feed per rev support lmao
        if self.config.feedrate_mode == "units_per_min":
            lines.append("G94 (feed per min)")
        else:
            raise ValueError(f"Unsupported feedrate mode: {self.config.feedrate_mode}")



        # DONT ACTUALLY DO THIS! 
        # need to tape tow to the mandrel before the program runs so we dont want it to home once the tow is taped. will have to home the machine before hand and use that reference point somehow

        # # home the machine
        # lines.append("G28 (home machine)")

        
        # format each line with line numbers maybe
        lines.append("")
        return [self._format_line(line) for line in lines]
    


    def _make_footer(self) -> list[str]:

        lines = [
            "",
            "M5 (stop spindle)", # i know we dont have one but idk
            "M30 (end program)"
        ]

        return [self._format_line(line) for line in lines]



    def _format_line(self, line: str) -> str:

        # do we actually want line numbers
        if not self.config.include_line_numbers or line == "":
            return line

        # add a line number
        numbered_line = f"N{self._line_number} {line}"

        # add increment to line number
        self._line_number += self.config.line_number_step
        return numbered_line


    def _validate_axis_table(self, axis_table: pd.DataFrame) -> None:

        # does the csv have all the right columns?
        required_columns = [
            self.config.spindle_column,
            self.config.z_column,
            self.config.x_column,
            self.config.head_column,
            self.config.feedrate_column,
        ]

        missing_columns = [
            column for column in required_columns
            if column not in axis_table.columns
        ]

        if missing_columns:
            raise ValueError(
                "Axis table is missing required columns: "
                + ", ".join(missing_columns)
            )
        


    def _make_motion_line(
        self,
        row: pd.Series
    ) -> str:
        
        axis_precision = self.config.axis_precision
        feedrate_precision = self.config.feedrate_precision

        a = row[self.config.spindle_column]
        z = row[self.config.z_column]
        x = row[self.config.x_column]
        b = row[self.config.head_column]
        f = row[self.config.feedrate_column]


        parts = [
            "G1",
            f"{self.config.spindle_axis_name}{a:.{axis_precision}f}",
            f"{self.config.z_axis_name}{z:.{axis_precision}f}",
            f"{self.config.x_axis_name}{x:.{axis_precision}f}",
            f"{self.config.head_axis_name}{b:.{axis_precision}f}",
            f"F{f:.{feedrate_precision}f}",
        ]

        line = " ".join(parts)

        # do we want to inlcude tension?
        if (
            self.config.output_tension_as_comment
            and self.config.tension_column is not None
            and self.config.tension_column in row.index
        ):
            
            tension = row[self.config.tension_column]
            line += f" ; tension_N={tension:.3f}"


        return self._format_line(line)




    def write_nc_file(
        self,
        input_csv_path: str | Path,
        output_gcode_path: str | Path
    ) -> None:
        
        self._line_number = self.config.line_number_start

        # read in csv as a pandas dataframe
        axis_table = pd.read_csv(input_csv_path)
        
        # does the csv have the right columns?
        self._validate_axis_table(axis_table)


        lines: list[str] = []

        lines.extend(self._make_header())


        for _, row in axis_table.iterrows():
            lines.append(self._make_motion_line(row))


        lines.extend(self._make_footer())

        output_gcode_path = Path(output_gcode_path)
        output_gcode_path.write_text("\n".join(lines), encoding="utf-8")