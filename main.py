from gcode_writer import GCodeWriterConfig, GCodeWriter
from axis_processor import AxisProcessorConfig, AxisProcessor


axis_processor_config = AxisProcessorConfig(
    x_clearance_mm=10.0,
    default_feedrate_mm_min=100.0,
    default_tension_n=20.0,
)

gcode_config  = GCodeWriterConfig(
    program_name="Test_Winding_Path",
    include_line_numbers=True,
)


axis_processor = AxisProcessor(axis_processor_config)

axis_processor.process_csv(
    input_path_csv="fibre_path.csv",
    output_axis_csv="axis_output.csv",
)


gcode_config  = GCodeWriterConfig(
    program_name="Test_Winding_Path",
    include_line_numbers=True,
)

writer = GCodeWriter(gcode_config )

writer.write_nc_file(
    input_csv_path="axis_output.csv",
    output_gcode_path="winding_path.nc"
)