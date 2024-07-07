from machine import UART  # type: ignore
import collections
import time

REPORT_HEADER = bytes.fromhex('AAFF0300')
REPORT_TAIL = bytes.fromhex('55CC')

data_queue = collections.deque((), 10)

uart = UART(2, tx=23, rx=21)
uart.init(256000, bits=8, parity=None, stop=1)

def parse_radar_data(serial_port_line):

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

# def create_uart(tx_pin_n, rx_pin_n):
#     uart = UART(2, tx=tx_pin_n, rx=rx_pin_n)
#     uart.init(256000, bits=8, parity=None, stop=1)
    # return uart

def read_single_radar_data(uart):
    while uart.any() == 0:
        pass
    serial_port_line = read_until(uart, REPORT_TAIL)
    print(f'got serial port line: {repr(serial_port_line)}')
    return serial_port_line

# def create_queue(length):
#     data_queue = collections.deque(maxlen=length)
#     return data_queue



# while True:
# #     data = uart.readline()
#     while uart.any() == 0:
#         pass
# #     serial_port_line = uart.read(50)
#     serial_port_line = read_until(uart, REPORT_TAIL)
#     print(f'got serial port line: {repr(serial_port_line)}')
#     all_target_values = read_radar_data(serial_port_line)
#     target1_x, target1_y, target1_speed, target1_distance_res, \
#         target2_x, target2_y, target2_speed, target2_distance_res, \
#         target3_x, target3_y, target3_speed, target3_distance_res \
#             = all_target_values
#     # Print the interpreted information for all targets
#     print(f'Target 1 x-coordinate: {target1_x} mm')
#     print(f'Target 1 y-coordinate: {target1_y} mm')
#     print(f'Target 1 speed: {target1_speed} cm/s')
#     print(f'Target 1 distance res: {target1_distance_res} mm')
# 
#     print(f'Target 2 x-coordinate: {target2_x} mm')
#     print(f'Target 2 y-coordinate: {target2_y} mm')
#     print(f'Target 2 speed: {target2_speed} cm/s')
#     print(f'Target 2 distance res: {target2_distance_res} mm')
# 
#     print(f'Target 3 x-coordinate: {target3_x} mm')
#     print(f'Target 3 y-coordinate: {target3_y} mm')
#     print(f'Target 3 speed: {target3_speed} cm/s')
#     print(f'Target 3 distance res: {target3_distance_res} mm')
# 
#     print('-' * 30)





# 
# 
# 
# 
# 
# 
# 
# 
# 
# 
# 
# 
# 
# 

import usocket as socket
import network
class WifiServer(hostname='ESP32_server'):
    def __init__(self):
        self.server_setup(hostname)
        
    def server_setup(self, hostname):
        self.wlan = network.WLAN(network.STA_IF)
        print('setting up wifi server, is wifi active:', self.wlan.active())
        if not self.wlan.isconnected():
                self.reconnect()
#         with open('wifi_server_password.txt') as f:
#             self.password = f.read().strip()
        self.server_ip = self.wlan.ifconfig()[0]
        print('server IP address:', self.server_ip)
        self.server_port = 1704
        self.addr = socket.getaddrinfo(self.server_ip, self.server_port)[0][-1]
        self.server_socket = socket.socket()
        self.server_socket.bind(self.addr)
        self.server_socket.setblocking(True)
        self.server_socket.settimeout(0.05)
        network.hostname('watchdog0')

        print('wifi server setup complete')

    def reconnect(self):
        print('wifi not connected, checking again and trying to reconnect')
        # wait and check for wifi connection with exponential backoff, for a total of about 4 minutes
        for i in range(8):
            if self.wlan.isconnected():
                return
            else:
                # exponential backoff
                time.sleep(1*(2**i))
                print('wifi not connected, trying again')
        # restart machine to rescan wireless networks and reconnect
        machine.reset()

    # def start_server(self):
    #     self.server_socket.listen(1)
    #     print('Server is started, listening on port', self.server_port)
    #     while True:   # define periodic check for wifi connection, and contingency if not
    #         if not self.wlan.isconnected():
    #             self.reconnect()
    #         try:
    #             client_socket, client_address = self.server_socket.accept()
    #         except Exception:
    #             print('wifi server timed out, restarting')
    #             continue
    #         print("Accepted connection from", client_address)
    #         input_data = client_socket.recv(256)
    #         if not input_data:
    #             print('got None input')
    #             input_data_str = ''
    #         else:
    #             print('got non-None input')
    #             input_data_str = input_data.decode() # receive data from client
    #         print(f'received from client: {input_data}')
    #         ### handling of input ###
    #         if input_data_str == '':
    #             print('got empty string, sending IMA')
    #             # send an IMA
    #             client_socket.send('I am alive'.encode())
    #         else:
    #             print('got nonempty string, sending ECHO')
    #             # echo all caps
    #             client_socket.send(input_data_str.upper().encode())
    #         print('response sent')
    #         time.sleep_ms(100)                
    #         client_socket.close() 
    #         print('socket closed')

    def start_radar_server(self):
        self.server_socket.listen(1)
        print('Server is started, listening on port', self.server_port)
        while True:   # define periodic check for wifi connection, and contingency if not
            time.sleep(2)
            # add a radar reading to the queue
            single_data_row = read_single_radar_data(uart)
            # all_target_values = parse_radar_data(single_data_row)
            data_queue.append(single_data_row)
            print(f'queue length: {len(data_queue)}')


            
            if not self.wlan.isconnected():
                self.reconnect()
            try:
                client_socket, client_address = self.server_socket.accept()
            except Exception:
                print('wifi server timed out, restarting')
                continue
            print("Accepted connection from", client_address)
            input_data = client_socket.recv(256)
            if not input_data:
                print('got None input')
                input_data_str = ''
            else:
                print('got non-None input')
                input_data_str = input_data.decode() # receive data from client
            print(f'received from client: {input_data}')
            ### handling of input ###
            if input_data_str.lower() == 'bdallack':
                print('got bdallack, sending radar data')
                # convert the queue to a bytearray
                data_queue_bytes = b''
                while data_queue:
                    temp_data = data_queue.popleft()
                    print(f'popped {repr(temp_data)}')
                    print(f'queue length: {len(data_queue)}')
                    data_queue_bytes += temp_data
                client_socket.send(data_queue_bytes)

                

            elif input_data_str == '':
                print('got empty string, sending IMA')
                # send an IMA
                client_socket.send('I am alive'.encode())
            else:
                print('got nonempty string, sending ECHO')
                # echo all caps
                client_socket.send(input_data_str.upper().encode())
            print('response sent')
            time.sleep_ms(100)                
            client_socket.close() 
            print('socket closed')




wfs = WifiServer()
wfs.start_radar_server()






