from machine import UART
REPORT_HEADER = bytes.fromhex('AAFF0300')
REPORT_TAIL = bytes.fromhex('55CC')

def read_radar_data(serial_port_line):
    # Check if the frame header and tail are present
    if REPORT_HEADER in serial_port_line and REPORT_TAIL in serial_port_line:
        # Interpret the target data
        if len(serial_port_line) == 30:
            target1_bytes = serial_port_line[4:12]
            target2_bytes = serial_port_line[12:20]
            target3_bytes = serial_port_line[20:28]
            all_targets_bytes = [target1_bytes, target2_bytes, target3_bytes]
            all_targets_data = []

            for target_bytes in all_targets_bytes:
                x = int.from_bytes(target_bytes[0:2], 'little')
                y = int.from_bytes(target_bytes[2:4], 'little')
                speed = int.from_bytes(target_bytes[4:6], 'little')
                distance_resolution = int.from_bytes(target_bytes[6:8], 'little')

                # Manually handle signed conversion
                if x >= 0x8000:
                    x = 0x8000 - x
                if y >= 0x8000:
                    y -= 0x8000
                if speed >= 0x8000:
                    speed = 0x8000-speed

                # Append target data to the list and flatten
                all_targets_data.extend([x, y, speed, distance_resolution])

            return tuple(all_targets_data)
        else:
            print("Serial port line corrupted - not 30 bytes long")
            return None
    else:
        print("Serial port line corrupted - header or tail not present")
        return None


def read_until(uart, terminator):
    buffer = bytearray()
    while True:
        byte = uart.read(1)
        if not byte:
            break  # Timeout or end of data
        buffer.extend(byte)
        if buffer.endswith(terminator):
            break
    return bytes(buffer)
    
uart = UART(2, tx=23, rx=21)
uart.init(256000, bits=8, parity=None, stop=1)

while True:
#     data = uart.readline()
    while uart.any() == 0:
        pass
#     serial_port_line = uart.read(50)
    serial_port_line = read_until(uart, REPORT_TAIL)
    print(f'got serial port line: {repr(serial_port_line)}')
    all_target_values = read_radar_data(serial_port_line)
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

    print('-' * 30)


