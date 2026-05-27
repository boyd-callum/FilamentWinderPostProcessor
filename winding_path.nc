N0 (Test_Winding_Path)
N1 G21 (mm)
N2 G90 (absolute positioning)
N3 G94 (feed per min)

N4 G1 A0.000 Z0.000 X42.000 B12.000 F500.0 ; tension_N=20.000
N5 G1 A3.200 Z0.400 X42.100 B12.400 F500.0 ; tension_N=20.000

N6 M5 (stop spindle)
N7 M30 (end program)