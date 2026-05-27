from gcode_writer import GCodeWriterConfig, GCodeWriter


config = GCodeWriterConfig(
    program_name="Test_Winding_Path",
    include_line_numbers=True,
)

writer = GCodeWriter(config)

writer.write_nc_file(
    input_csv_path="axis_output.csv",
    output_gcode_path="winding_path.nc"
)