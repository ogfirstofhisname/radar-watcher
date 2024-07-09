
from machine import UART  # type: ignore
import time

REPORT_HEADER = bytes.fromhex('AAFF0300')
REPORT_TAIL = bytes.fromhex('55CC')

def timestamp_float():
    # time since epoch in seconds with microsecond precision, equivalent to CPython's time.time()
    nanoseconds = time.time_ns()
    # Convert nanoseconds to microseconds
    microseconds = nanoseconds // 1000
    # Convert microseconds to seconds (as a float)
    seconds = 1.0*microseconds / 1_000_000
#     seconds = seconds + 946684800.0  # correction from ESP32 epoch to Unix epoch
    return seconds

class HLKLD2450Radar():
    def __init__(self, uart_rx_pin, uart_tx_pin):
        '''
        Initialize the radar sensor with the given UART pins.

        Args:
        uart_rx_pin: int, the RX pin for the UART
        uart_tx_pin: int, the TX pin for the UART
        '''
        self.uart_rx_pin = uart_rx_pin
        self.uart_tx_pin = uart_tx_pin
        self.uart = UART(2, tx=self.uart_tx_pin, rx=self.uart_rx_pin)
        self.uart.init(256000, bits=8, parity=None, stop=1)

    def _read_until(self, terminator):
        buffer = bytearray()
        while True:
            byte = self.uart.read(1)
            if not byte:
                break # Timeout or end of data
            buffer.extend(byte)
            if buffer.endswith(terminator):
                break
        return bytes(buffer)

    def read_single_radar_data(self, timeout_ms=1000):
        '''
        Reads without parsing a single 'row' of radar data.

        Returns:
        radar_data: bytes, the radar data read
        '''
        # Calculate deadline for operation
        deadline = time.ticks_add(time.ticks_ms(), timeout_ms)
        while self.uart.any() == 0:
            if time.ticks_diff(deadline, time.ticks_ms()) < 0:
                print('uard read timed out')
                return None
        serial_port_line = self._read_until(REPORT_TAIL)
        return serial_port_line

    def read_single_sensor_data(self):
        single_data_row = self.read_single_radar_data()
        # if data is None, return None
        if single_data_row is None:
            return None
        # if data is not 30 bytes long, return None
        if len(single_data_row) != 30:
            return None
        # if data does not contain the header and tail, return None
        if REPORT_HEADER not in single_data_row or REPORT_TAIL not in single_data_row:
            return None

        return single_data_row

    def parse_radar_data(self, radar_data):
        '''
        A convenience method to parse the radar data into a dictionary of target values.
        Not used in the server-client implementation.
        Adapted to micropython from https://github.com/csRon/HLK-LD2450.

        Args:
        radar_data: bytes, a single 30-byte read from the radar sensor

        Returns:
        target_values: dict, a dictionary of target values
        '''
        # Check if the frame header and tail are present
        if REPORT_HEADER in radar_data and REPORT_TAIL in radar_data:
            # Interpret the target data
            if len(radar_data) == 30:
                target1_bytes = radar_data[4:12]
                target2_bytes = radar_data[12:20]
                target3_bytes = radar_data[20:28]
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
                data_dict = {
                    'target1_x': all_targets_data[0],
                    'target1_y': all_targets_data[1],
                    'target1_speed': all_targets_data[2],
                    'target1_distance_resolution': all_targets_data[3],
                    'target2_x': all_targets_data[4],
                    'target2_y': all_targets_data[5],
                    'target2_speed': all_targets_data[6],
                    'target2_distance_resolution': all_targets_data[7],
                    'target3_x': all_targets_data[8],
                    'target3_y': all_targets_data[9],
                    'target3_speed': all_targets_data[10],
                    'target3_distance_resolution': all_targets_data[11]
                }

                return data_dict
            
            else:
                print("Serial port line corrupted - not 30 bytes long")
                return None
        else:
            print("Serial port line corrupted - header or tail not present")
            return None


# def parse_radar_data(serial_port_line):

#     # Check if the frame header and tail are present
#     if REPORT_HEADER in serial_port_line and REPORT_TAIL in serial_port_line:
#         # Interpret the target data
#         if len(serial_port_line) == 30:
#             target1_bytes = serial_port_line[4:12]
#             target2_bytes = serial_port_line[12:20]
#             target3_bytes = serial_port_line[20:28]
#             all_targets_bytes = [target1_bytes, target2_bytes, target3_bytes]
#             all_targets_data = []

#             for target_bytes in all_targets_bytes:
#                 x = int.from_bytes(target_bytes[0:2], 'little')
#                 y = int.from_bytes(target_bytes[2:4], 'little')
#                 speed = int.from_bytes(target_bytes[4:6], 'little')
#                 distance_resolution = int.from_bytes(target_bytes[6:8], 'little')

#                 # Manually handle signed conversion
#                 if x >= 0x8000:
#                     x = 0x8000 - x
#                 if y >= 0x8000:
#                     y -= 0x8000
#                 if speed >= 0x8000:
#                     speed = 0x8000-speed

#                 # Append target data to the list and flatten
#                 all_targets_data.extend([x, y, speed, distance_resolution])

#             return tuple(all_targets_data)
#         else:
#             print("Serial port line corrupted - not 30 bytes long")
#             return None
#     else:
#         print("Serial port line corrupted - header or tail not present")
#         return None
