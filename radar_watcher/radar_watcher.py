# radar_watcher.py
# based on https://github.com/csRon/HLK-LD2450/

### see if we get anything from UART0
import serial, time
serial_port = '/dev/ttyS3'

# def read_from_uart():
#     # Open the serial port. Adjust the port name as necessary.
#     ser = serial.Serial(serial_port, 256000, timeout=1)
    
#     try:
#         while True:
#             if ser.in_waiting > 0:
#                 # Read a line from the serial interface
#                 line = ser.readline()
#                 # print(f"Received raw: {line}")
#                 # decode as hex
#                 line = line.hex()
#                 line = line.strip()
#                 print(f"Received: {line}")
#             else:
#                 print("Waiting for data...")
#                 time.sleep(0.1)
#     except KeyboardInterrupt:
#         print("Exiting...")
#     finally:
#         ser.close()

# read_from_uart()
# exit()
### if that works, let's use it



import serial_protocol  # from https://github.com/csRon/HLK-LD2450/
import serial
import threading
import queue

# Open the serial port
ser = serial.Serial(serial_port, 256000, timeout=1)

# ### or ALTERNATIVELY create a thread-safe queue and read into it in the background ###
# def serial_reader():
#     ser = serial.Serial(serial_port, 256000, timeout=1)

#     while True:
#         data = ser.read_until(serial_protocol.REPORT_TAIL)
#         data_queue.put(data)

# data_queue = queue.Queue()

# # Create and start the serial reader thread
# serial_thread = threading.Thread(target=serial_reader)
# serial_thread.daemon = True
# serial_thread.start()
# ###  ###

try:
    # while True:
    data_lines = []
    t0 = time.time()
    ser.reset_input_buffer()
    filename = f"radar_data.bin"
    for _ in range(1000):
        # Read a line from the serial port
        serial_port_line = ser.read_until(serial_protocol.REPORT_TAIL)
        data_lines.append(serial_port_line)
        print(repr(serial_port_line))
        # ### or ALTERNATIVELY ###
        # serial_protocol_line = data_queue.get()
        # ###  ###
        all_target_values = serial_protocol.read_radar_data(serial_port_line)
        
        if all_target_values is None:
            continue

        target1_x, target1_y, target1_speed, target1_distance_res, \
        target2_x, target2_y, target2_speed, target2_distance_res, \
        target3_x, target3_y, target3_speed, target3_distance_res \
            = all_target_values

        # # Print the interpreted information for all targets
        # print(f'Target 1 x-coordinate: {target1_x} mm')
        # print(f'Target 1 y-coordinate: {target1_y} mm')
        # print(f'Target 1 speed: {target1_speed} cm/s')
        # print(f'Target 1 distance res: {target1_distance_res} mm')

        # print(f'Target 2 x-coordinate: {target2_x} mm')
        # print(f'Target 2 y-coordinate: {target2_y} mm')
        # print(f'Target 2 speed: {target2_speed} cm/s')
        # print(f'Target 2 distance res: {target2_distance_res} mm')

        # print(f'Target 3 x-coordinate: {target3_x} mm')
        # print(f'Target 3 y-coordinate: {target3_y} mm')
        # print(f'Target 3 speed: {target3_speed} cm/s')
        # print(f'Target 3 distance res: {target3_distance_res} mm')

        # print('-' * 30)
    t1 = time.time()
    print(f"Time elapsed: {t1 - t0} seconds")
    with open(filename, 'wb') as f:
        for line in data_lines:
            f.write(line)
            # add a newline
            f.write(b'\n')

except KeyboardInterrupt:
    # Close the serial port on keyboard interrupt
    ser.close()
    print("Serial port closed.")
