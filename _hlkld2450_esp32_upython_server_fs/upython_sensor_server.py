import usocket as socket  # type: ignore
import network  # type: ignore
from wifi_utils import wifi_login_at_startup as wlas
import time
import machine  # type: ignore
import collections
import struct

def timestamp_float():
    # time since epoch in seconds with microsecond precision, equivalent to CPython's time.time()
    nanoseconds = time.time_ns()
    # Convert nanoseconds to microseconds
    microseconds = nanoseconds // 1000
    # Convert microseconds to seconds (as a float)
    seconds = 1.0*microseconds / 1_000_000
#     seconds = seconds + 946684800.0  # correction from ESP32 epoch to Unix epoch
    return seconds

class WifiSensorServer():
    def __init__(self, hostname='ESP32_server', port=1704, poll_wait_time=0.05, queue_size=100, **sensor_addr_args):
        self.sensor_setup(**sensor_addr_args)
        self.server_setup(hostname, port, poll_wait_time)
        # initialize empty queue
        self.data_queue = collections.deque((), queue_size)   # TODO: move this functionality to the sensor object
        
    def server_setup(self, hostname, port, poll_wait_time):
        # set up network connection
        success, wlan = wlas.connect_to_wifi(hostname)
        if not success or wlan is not None:
            self.wlan = wlan
        else:
            print('could not connect to wifi, exiting')
            time.sleep_ms(5000)
            machine.reset()
        print('setting up wifi server, is wifi active:', self.wlan.active())
        if not self.wlan.isconnected():
                self.reconnect()
        self.server_ip = self.wlan.ifconfig()[0]
        print('server IP address:', self.server_ip)
        self.server_port = port
        self.hostname = hostname

        # set up server socket
        self.poll_wait_time = poll_wait_time
        self.addr = socket.getaddrinfo(self.server_ip, self.server_port)[0][-1]
        self.server_socket = socket.socket()
        self.server_socket.bind(self.addr)
        self.server_socket.setblocking(True)
        self.server_socket.settimeout(self.poll_wait_time)
        print(f'socket timeout set to {self.poll_wait_time}')
        network.hostname(self.hostname)

#         # sync time from network for accurate timestamps
#         success = self.sync_time_from_network()
#         if not success:
#             print('could not sync time from network, timestamps are incorrect')
#         else:
#             print('time synced from network:', time.localtime())
        print('wifi server setup complete')

    def reconnect(self):
        # waits for wifi connection, if not connected, restarts machine
        print('wifi not connected, checking again and trying to reconnect')
        # wait and check for wifi connection 5 times with wait time of 1 second
        for i in range(5):
            if self.wlan.isconnected():
                return
            else:
                time.sleep_ms(1000)
                print('wifi not connected, trying again')
        # restart machine to rescan wireless networks and reconnect
        machine.reset()

    def convert_queue_to_bytes(self):
        # data_queue_bytes = b''
        # while self.data_queue:
        #     temp_data = self.data_queue.popleft()
        #     # print(f'popped {repr(temp_data)}, queue length: {len(self.data_queue)}')
        #     data_queue_bytes += temp_data

        # Define the format string for a single tuple (timestamp, data)
        # 'd' for double (float) and '30s' for 30-byte bytes
        tuple_format = 'd30s'

        # Define the format string for the entire deque + the final timestamp
        # Assuming we have n elements in the deque
        def get_format_string(n):
            return f'{tuple_format * n}d'

        # # Example deque of tuples
        # data_deque = deque([
        #     (1627889187.123, b'abcdefghijklmnopqrstuvwxyz1234'),
        #     (1627889190.456, b'abcdefghijklmnopqrstuvwxyz5678')
        # ])

        # Serialize the deque
        serialized_data = bytearray()

        # Add each (timestamp, data) tuple to the serialized data
        while self.data_queue:
            timestamp, data = self.data_queue.popleft()
            serialized_data.extend(struct.pack(tuple_format, timestamp, data))

        # Add the final serialization timestamp
        serialization_timestamp = timestamp_float()
        # convert this timestamp to bytes
        # float_bytes = struct.pack('f', my_float)
        # serialization_timestamp_bytes = struct.pack('d', serialization_timestamp)
        serialized_data.extend(struct.pack('d', serialization_timestamp))

        # # Print the serialized binary data
        # print(serialized_data)

        # # Example of deserializing the data back
        # # First, calculate the number of tuples
        # n = len(data_deque)

        # # Get the format string for deserialization
        # format_string = get_format_string(n)

        # # Deserialize the data
        # deserialized_data = struct.unpack(format_string, serialized_data)

        # # Extract the tuples and the final timestamp
        # deserialized_tuples = [
        #     (deserialized_data[i*2], deserialized_data[i*2 + 1])
        #     for i in range(n)
        # ]
        # final_timestamp = deserialized_data[-1]

        # print(deserialized_tuples)
        # print(final_timestamp)
        return serialized_data


    def start_server(self):
        # TODO add a periodic sync time from network with long period

        # start server listening on the port
        self.server_socket.listen(1)    # only one connection at a time
        print('Server is started, listening on port', self.server_port)
        print('moving on to main loop')
        # main loop: read sensor data, check wifi connection, and process client requests (or time out and continue, if no client request)
        while True:
            # TODO add a periodic sync time from network with long period

            # read sensor into queue
            single_data_row = self.read_single_sensor_data()   # TODO make this a generic sensor read
            if single_data_row is None:
                print('sensor read failed')
                continue
            else:
                self.data_queue.append(single_data_row)
                print(f'queue length: {len(self.data_queue)}')

            
            # verify wifi connection
            if not self.wlan.isconnected():
                self.reconnect()
            
            # see if there's an incoming connection from a client
            try:
                client_socket, client_address = self.server_socket.accept()
            except Exception:
                # if timed out, just continue: there is no client request
                print('timed out, no client request')
                continue

            # if not timed out, process the client request
            print("Accepted connection from", client_address)
            input_data = client_socket.recv(1024)
            if not input_data:
                # print('got None input')
                input_data = ''
            else:
                # print('got non-None input')
                input_data = input_data.decode() # received string from client
            print(f'received input from client: {input_data}')

            # process the string and send a response
            # if empty string, send IMA
            if input_data == '':
                print('got empty string, sending IMA')
                # send an IMA
                client_socket.send('IMA'.encode())
            # if 'get', just send data
            elif input_data == 'get':  # TODO: move this functionality to the sensor object
                print('got get, sending data')
                # convert the queue to a bytearray and send it
                data_queue_bytes = self.convert_queue_to_bytes()
                # data_queue_bytes = b''
                # while self.data_queue:
                #     temp_data = self.data_queue.popleft()
                #     # print(f'popped {repr(temp_data)}, queue length: {len(self.data_queue)}')
                #     data_queue_bytes += temp_data
                client_socket.send(data_queue_bytes)
#                 self.data_queue.clear()  # TODO: move this functionality to the sensor object

                print('data sent')
            else:
                # send ECHO
                print('got nonempty, non-get. sending ECHO')
                # echo all caps
                client_socket.send(input_data.upper().encode())
                print('ECHO sent')
                # additionally, if 'clear', clear the queue
                if input_data == 'clear':
                    print('got clear, clearing queue')
                    # clear queue
                    while self.data_queue:   # TODO: move this functionality to the sensor object
                        self.data_queue.popleft()
                    print(f'queue length: {len(self.data_queue)}')
                # if 'reset', reset the ESP32
                elif input_data == 'reset':
                    # close socket and reset machine
                    print('got reset, resetting machine')
                    time.sleep_ms(50)
                    client_socket.close() 
                    print('socket closed')
                    time.sleep_ms(50)
                    # reset machine
                    machine.reset()
                    time.sleep_ms(500)
            time.sleep_ms(10)                
            client_socket.close() 
            print('socket closed')

    def sensor_setup(self, **sensor_addr_args):
        '''
        Set up the sensor for reading. This method is meant to be overridden by subclasses.
        '''
        pass

    def read_single_sensor_data(self):
        '''
        Read a single 'row' of sensor data and return a tuple of (data, timestamp).
        This method is meant to be overridden by subclasses.

        Returns:
        data: str or bytes, the sensor data
        timestamp: float, the timestamp of the data

        '''
        return timestamp_float(), b''

    def sync_time_from_network(self, single_try=False):
        '''
        Sync the ESP32's internal RTC with the network time, using the ntptime module.

        Args:
        single_try: bool, if True, only try once to sync time. If False, try 5 times with increasing wait times for a total of about 60 seconds.

        Returns:
        success: bool, True if time was successfully synced, False otherwise
        '''
        for i in range(5):
            try:
                import ntptime  # type: ignore
                ntptime.settime() # set the rtc datetime from the remote server
                return True
            except Exception:
                if single_try:
                    break
                time.sleep(1*2**(i+1))
        print('could not sync time from network')
        return False

class WifiRadarServer(WifiSensorServer):
    def sensor_setup(self, uart_rx_pin=17, uart_tx_pin=16):
        from ld2450_radar import HLKLD2450Radar
        self.sensor = HLKLD2450Radar(uart_rx_pin, uart_tx_pin)

    def read_single_sensor_data(self):
        single_data_row = self.sensor.read_single_radar_data()
        return timestamp_float(), single_data_row



