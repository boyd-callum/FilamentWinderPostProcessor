from gcode_writer import GCodeWriterConfig, GCodeWriter
from axis_processor import AxisLimit, AxisProcessorConfig, AxisProcessor, TensionConfig


tension_config = TensionConfig(
    mode="linear_by_layer",
    start_tension_n=25.0,
    end_tension_n=20.0
)

axis_processor_config = AxisProcessorConfig(
    x_clearance_mm=10.0,
    default_feedrate_mm_min=500.0,
    spindle_limit=AxisLimit("A", -1e9, 1e9),
    z_limit=AxisLimit("Z", 0.0, 2500.0),
    x_limit=AxisLimit("X", 0.0, 300.0),
    head_limit=AxisLimit("B", -180.0, 180.0),
    tension_config=tension_config
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