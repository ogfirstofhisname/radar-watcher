import usocket as socket
import network
from wifi_utils import wifi_login_at_startup as wlas
import time
import machine  # type: ignore
import collections

def timestamp():
    # time since epoch in seconds with microsecond precision, equivalent to CPython's time.time()
    nanoseconds = time.time_ns()
    # Convert nanoseconds to microseconds
    microseconds = nanoseconds // 1000
    # Convert microseconds to seconds (as a float)
    seconds = microseconds / 1_000_000
    return seconds

class WifiSensorServer():
    def __init__(self, hostname='ESP32_server', port=1704, poll_wait_time=0.05, queue_size=100, **sensor_addr_args):
        self.sensor_setup(**sensor_addr_args)
        self.server_setup(hostname, port, poll_wait_time)
        # initialize empty queue
        self.data_queue = collections.deque((), maxlen=queue_size)
        
    def server_setup(self, hostname, port, poll_wait_time):
        wlas.connect_to_wifi(hostname)
        # self.wlan = network.WLAN(network.STA_IF)
        print('setting up wifi server, is wifi active:', self.wlan.active())
        if not self.wlan.isconnected():
                self.reconnect()
#         with open('wifi_server_password.txt') as f:
#             self.password = f.read().strip()
        self.server_ip = self.wlan.ifconfig()[0]
        print('server IP address:', self.server_ip)
        self.server_port = port
        self.hostname = hostname
        self.poll_wait_time = poll_wait_time
        self.addr = socket.getaddrinfo(self.server_ip, self.server_port)[0][-1]
        self.server_socket = socket.socket()
        self.server_socket.bind(self.addr)
        self.server_socket.setblocking(True)
        self.server_socket.settimeout(self.poll_wait_time)
        network.hostname(self.hostname)
        success = self.sync_time_from_network()
        if not success:
            print('could not sync time from network, timestamps are incorrect')
        else:
            print('time synced from network:', time.localtime())
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

    def start_server(self):
        self.server_socket.listen(1)    # only one connection at a time
        print('Server is started, listening on port', self.server_port)
        while True:   # define periodic check for wifi connection, and contingency if not
            # read sensor into queue
            single_data_row = self.read_single_sensor_data()   # TODO make this a generic sensor read
            self.data_queue.append(single_data_row)
            print(f'queue length: {len(self.data_queue)}')

            
            # verify wifi connection
            if not self.wlan.isconnected():
                self.reconnect()
            
            # see if there's an incoming connection from a client
            try:
                client_socket, client_address = self.server_socket.accept()
            except Exception:
                # if timed out, just continue
                # print('wifi server timed out, restarting')
                continue

            # if not timed out, process the client request
            print("Accepted connection from", client_address)
            input_data = client_socket.recv(1024)
            if not input_data:
                print('got None input')
                input_data = ''
            else:
                print('got non-None input')
                input_data = input_data.decode() # received string from client
            print(f'received from client: {input_data}')

            # process the string and send a response
            # if empty string, send IMA
            if input_data == '':
                print('got empty string, sending IMA')
                # send an IMA
                client_socket.send('I am alive'.encode())
            # if 'get', just send data
            elif input_data == 'get':
                print('got get, sending data')
                # send data
                # TODO
            else:
                # send ECHO
                print('got non-get, sending ECHO')
                # echo all caps
                client_socket.send(input_data.upper().encode())
                print('response sent')
                # additionally, if 'clear', clear the queue
                if input_data == 'clear':
                    print('got clear, clearing queue')
                    # clear queue
                    self.data_queue.clear()
                # if 'reset', reset the machine
                elif input_data == 'reset':
                    print('got reset, resetting machine')
                    client_socket.send(input_data.upper().encode())
                    time.sleep_ms(50)
                    client_socket.close() 
                    print('socket closed')
                    time.sleep_ms(50)
                    # reset machine
                    machine.reset()
            time.sleep_ms(100)                
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
        return '', timestamp()

    def sync_time_from_network(self):
        for i in range(5):
            try:
                import ntptime  # type: ignore
                ntptime.settime() # set the rtc datetime from the remote server
                return True
            except Exception:
                time.sleep(1*2**(i+1))
        print('could not sync time from network')
        return False

class WifiRadarServer(WifiSensorServer):
    def sensor_setup(self, uart_rx_pin=17, uart_tx_pin=16):
        from ld2450_radar import HLKLD2450Radar
        self.sensor = HLKLD2450Radar(uart_rx_pin, uart_tx_pin)

    def read_single_sensor_data(self):
        single_data_row = self.sensor.read_single_radar_data()
        return single_data_row, timestamp()
