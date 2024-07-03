import serial_protocol
import time


filename = 'radar_data.bin'
data_lines = []
# open file as binary and read all lines into a list
with open(filename, 'rb') as f:
    for line in f:
        line = line.strip()
        data_lines.append(line)
# print all the lines
for serial_port_line in data_lines:
    print(repr(serial_port_line))
    all_target_values = serial_protocol.read_radar_data(serial_port_line)
        
    if all_target_values is None:
        continue

    target1_x, target1_y, target1_speed, target1_distance_res, \
    target2_x, target2_y, target2_speed, target2_distance_res, \
    target3_x, target3_y, target3_speed, target3_distance_res \
        = all_target_values

    # Print the interpreted information for all targets
    print(f'Target 1 x-coordinate: {target1_x} mm')
    print(f'Target 1 y-coordinate: {target1_y} mm')
    print(f'Target 1 speed: {target1_speed} cm/s')
    print(f'Target 1 distance res: {target1_distance_res} mm')

    print(f'Target 2 x-coordinate: {target2_x} mm')
    print(f'Target 2 y-coordinate: {target2_y} mm')
    print(f'Target 2 speed: {target2_speed} cm/s')
    print(f'Target 2 distance res: {target2_distance_res} mm')

    print(f'Target 3 x-coordinate: {target3_x} mm')
    print(f'Target 3 y-coordinate: {target3_y} mm')
    print(f'Target 3 speed: {target3_speed} cm/s')
    print(f'Target 3 distance res: {target3_distance_res} mm')
    time.sleep(0.09)