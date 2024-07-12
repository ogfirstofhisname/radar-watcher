import socket, time, struct
from threading import Lock, Thread
from collections import deque
from serial_protocol.serial_protocol import read_radar_data
import sys
import pandas as pd

SOCKET_DEFAULT_TIMEOUT = 3

def get_total_size(obj, seen=None):
    """Recursively finds the total size of an object, including its nested elements."""
    if seen is None:
        seen = set()

    obj_id = id(obj)
    if obj_id in seen:
        return 0

    seen.add(obj_id)
    size = sys.getsizeof(obj)

    if isinstance(obj, dict):
        size += sum([get_total_size(v, seen) for v in obj.values()])
        size += sum([get_total_size(k, seen) for k in obj.keys()])
    elif isinstance(obj, (list, tuple, set, deque)):
        size += sum([get_total_size(i, seen) for i in obj])

    return size


class WifiClient():
    def __init__(self, hostname:str, port:int, socket_timeout=SOCKET_DEFAULT_TIMEOUT):
        self.server_hostname = hostname
        self.server_port = port
        # create locks for server status, server IP, and last alive time
        self.server_status_lock = Lock()
        self.server_ip_lock = Lock()
        self.last_alive_time_lock = Lock()
        # initialize server status, server IP, and last alive time
        with self.server_status_lock:
            self.server_status = None
        with self.server_ip_lock:
            self.server_ip = None
        with self.last_alive_time_lock:
            self.last_alive_time = None
        self._socket_timeout = socket_timeout
        self.init_client()
    
    def init_client(self, check_online=False) -> tuple[bool, str]:
        # puts the client in a "ready for transaction" state

        # attempt to get the server's IP address
        ip = self._get_ip_address(self.server_hostname)
        if ip is not None:
            with self.server_ip_lock:
                self.server_ip = ip
        else:
            return False, 'hostname not found in network'
        # # create a socket if not already created
        # if self.socket is None:
        #     self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #     # set timeout for socket operations
        #     socket.setdefaulttimeout(3)  # TODO change to about 10 for normal use
        #     print('socket created and set with timeout')
        if check_online:
            # check if the server is online
            is_online = self.check_if_online()
            if not is_online:
                return False, 'Server not online'
        return True, ''
            
        
    # def _online(self):
    #     # called when the server is known to be online
    #     with self.server_status_lock:
    #         self.server_status = 'online'

    # def _offline(self):
    #     # called when the server is known to be offline
    #     with self.server_status_lock:
    #         self.server_status = 'offline'

    def _alive(self):
        # called when the server is instantaneously known to be alive, i.e. a response was received from the server
        with self.server_status_lock:
            self.last_alive_time = time.time()

    # def is_online(self):
    #     '''
    #     Returns True if the server is online, False otherwise.

    #     Returns:
    #     bool: True if the server is online, False otherwise.
    #     '''
    #     with self.server_status_lock:
    #         return self.server_status == 'online'
        
    def check_if_online(self):
        '''
        Actively checks if the server is online, sets the server status accordingly, and returns the result.
        '''
        # send 'echo' to server and check if the response is 'ECHO'
        is_online = False
        # if self.socket is None:
        #     self.init_client()
        try:
            success, data, receive_timestamp = self.transact_with_server('echo')
            if success:
                is_online = data.decode() == 'ECHO'
        except Exception as e:
            pass
        # if is_online:
        #     # self._online()
        #     self._alive()
        else:
            # self._offline()
            pass
        return is_online
        
    def time_since_last_alive(self, do_not_round=False):
        '''
        Returns the time since the server was last known to be alive, in seconds.

        Returns:
        float: The time since the server was last known to be alive, in seconds.
        '''
        with self.last_alive_time_lock:
            lat = self.last_alive_time
        if lat is None:
            return None
        else:
            if not do_not_round:
                return round(time.time() - lat, 3)
            return time.time() - lat
              
    # def was_alive_recently(self, timeout=10):
    #     with self.last_alive_time_lock:
    #         lat = self.last_alive_time
    #     if lat is None:
    #         return False
    #     else:
    #         return time.time() - lat < timeout

    def _get_ip_address(self, hostname):
        try:
            ip = socket.gethostbyname(hostname)
            with self.server_ip_lock:
                self.server_ip = ip
            # self._online()
            return ip
        except socket.gaierror:
            # print("Invalid hostname. Please check the hostname and try again.")
            # self._offline()
            return None

    def _wait(self):
        time.sleep(0.01)

    def transact_with_server(self, client_message:str, timeout=None):
        '''
        Takes a string argument and sends it to the server, returning the server's response as bytes.

        Args:
        client_message (str): The message to be sent to the server.
        timeout (float): The timeout for the socket operations.

        Returns:
        bytes: The response from the server.
        '''
        # TODO add try-except and a retry loop with increasing waits until an exception is raised
        # TODO put the socket into an attribute and reuse it
        success = False
        receive_timestamp = None
        # if self.socket is None:
        #     raise Exception('Socket not initialized')
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            # with self.socket as client_socket:
                
                if timeout is not None:
                    client_socket.settimeout(timeout)  # Set the timeout for the socket
                else:
                    client_socket.settimeout(self._socket_timeout)
                # print('connecting socket...')
                client_socket.connect((self.server_ip, self.server_port))
                # print('connected to server')
                self._wait()
                client_socket.send(client_message.encode())  # TODO implement timeout
                # print(f'sent message: {client_message}')
                self._wait()

                data = b""
                while True:
                    packet = client_socket.recv(256)  # TODO change to 32768 for normal use
                    if not packet: 
                        break
                    data += packet
                    # print(f'got packet: {repr(packet)}')
                    self._wait()
                # print(f'got raw data: {repr(data)}')
                self._alive()
                # self._online()
                success = True
                receive_timestamp = time.time()
        except socket.timeout:
            # response was not sent promptly. The server may be in some fault state, or simply busy.
            # print('Socket timed out')
            # data = b''
            data = None
        except ConnectionRefusedError:
            # the server is not accepting connections, may be in some fault state.
            # print('Connection refused')
            # data = b''
            data = None
            # self._offline()
        # except ConnectionResetError:
        #     print('Connection reset')
        #     data = b''
        #     self._offline()
        # except ConnectionAbortedError:
        #     print('Connection aborted')
        #     data = b''
        #     self._offline()
        except Exception as e:
            print(f'An unusual exception occurred: {e}')
            # data = b''
            data = None
            
        return success, data, receive_timestamp
    
    def get_ip(self):
        with self.server_ip_lock:
            return self.server_ip
    

class HLKLD2450RemoteSensor():
    # includes a wifi client within it
    def __init__(self, hostname:str, port:int, len_short_queue=330, len_long_queue=100000, socket_timeout=SOCKET_DEFAULT_TIMEOUT):
        self.name = hostname
        self.client = WifiClient(hostname, port, socket_timeout)
        self.thread = None
        # set up queues for data
        self.short_data_queue = deque(maxlen=len_short_queue)
        self.long_data_queue = deque(maxlen=len_long_queue)
        # set up locks for queues
        self.short_queue_lock = Lock()
        self.long_queue_lock = Lock()
        # set up running flag and lock
        self.running = False
        self.running_lock = Lock()
        # set up an fps attribute and lock
        self._fps = None
        self.fps_lock = Lock()
        # print('created client')
        # set global socket timeout
        # socket.setdefaulttimeout(3)  # TODO change to about 10 for normal use



    def run_remote_sensor(self, loop_hold_time=0.5):
        # set running flag to True
        with self.running_lock:
            self.running = True
        # connect and clear buffer loop
        # print(f'starting the connection and update loop')
        while True:
            # check if running flag is False
            with self.running_lock:
                if not self.running:
                    break
            # connect and update
            success, error_msg = self.connect_and_update()
            if not success:
                # failed to connect, can't go into the read data loop, so sleep for a bit and try again
                # print(f'Failed to connect and update')
                time.sleep(1)
                continue
            # clear the remote sensor's buffer
            self.clear_remote_buffer()
            # set up fps calculation
            _fps_timestamp_queue = deque(maxlen=10)
            _fps_n_put_in_queues_queue = deque(maxlen=10)
            with self.fps_lock:
                self._fps = None
            # read data loop
            # print(f'starting the read data loop')
            while True:
                # check if running flag is False
                with self.running_lock:
                    if not self.running:
                        break
                # read data
                # print('reading data...')
                success, data, receive_timestamp = self.read_data()
                # print(f'success: {success}, data: {data[0:4] if data is not None else None}, receive_timestamp: {receive_timestamp}')
                if not success:
                    # break out of the read data loop back into the connect and update loop
                    # print('Failed to read data, breaking out of read data loop') # this is often the case when the server is online but is still initializing
                    with self.fps_lock:
                        self._fps = None
                    time.sleep(1)
                    break
                
                # put data into queues
                n_put_in_queues = self.put_data_into_queues(data, receive_timestamp)
                # update fps queues
                _fps_timestamp_queue.append(receive_timestamp)
                _fps_n_put_in_queues_queue.append(n_put_in_queues)
                # calculate fps
                if len(_fps_timestamp_queue) >= 2:
                    # calculate instantaneous fps
                    total_n_put_in_queues = sum(_fps_n_put_in_queues_queue)
                    total_time = _fps_timestamp_queue[-1] - _fps_timestamp_queue[0]
                    with self.fps_lock:
                        self._fps = 1.0*total_n_put_in_queues / total_time
                # sleep for a bit
                time.sleep(loop_hold_time)

    def get_fps(self, do_not_round=False):
        with self.fps_lock:
            temp_fps = self._fps
        if not do_not_round:
            if temp_fps is not None:
                return round(temp_fps, 3)
        return temp_fps

    def connect_and_update(self):
        success, error_msg = self.client.init_client(check_online=True)
        return success, error_msg

    def clear_remote_buffer(self):
        success, data, receive_timestamp = self.client.transact_with_server('clear')
        try:
            success = success and data.decode() == 'CLEAR'
        except Exception as e:
            # print(f'Exception occurred in clear_remote_buffer(): {e}')
            success = False
        if not success:
            # print('Failed to clear remote buffer')
            return False
        return True
        
    def read_data(self):
        success, response, receive_timestamp = self.client.transact_with_server('get')
        if not success:
            return False, None, None
        return True, response, receive_timestamp

    def put_data_into_queues(self, data, receive_timestamp):
        n_put_in_queues = 0
        data_deque, final_timestamp = self.deserialize_data(data, receive_timestamp)
        with self.short_queue_lock:
            # self.short_data_queue.extend(data_deque)
            for data_time_tuple in data_deque:
                self.short_data_queue.append(data_time_tuple)
                n_put_in_queues += 1
        with self.long_queue_lock:
            # self.long_data_queue.extend(data_deque)
            for data_time_tuple in data_deque:
                self.long_data_queue.append(data_time_tuple)
                # print(f'data tuple appended to long queue: {data_time_tuple}, size: {self.long_data_queue.__sizeof__()} bytes')
        # print(f'data put into queues. len(short): {len(self.short_data_queue)}, len(long): {len(self.long_data_queue)}')
        return n_put_in_queues

    # TODO pass all the 'alive' functionality to the sensor object...?

    def get_short_queue(self):
        with self.short_queue_lock:
            return self.short_data_queue.copy()
        
    def get_long_queue(self):
        with self.long_queue_lock:
            return self.long_data_queue.copy()
        
    def get_short_queue_df(self):
        short_queue = self.get_short_queue()
        if short_queue is None:
            return None
        # initialize an empty dataframe
        # df = pd.DataFrame()
        # iterate through the short queue and append each element to the dataframe
        # len_short_queue = self.get_short_queue_length()
        # t0 = time.time()
        # for data_time_tuple in short_queue:
        #     parsed_dict = self.parse_radar_data(data_queue_element=data_time_tuple)
        #     if parsed_dict is None:
        #         continue
        #     df = df.append(parsed_dict, ignore_index=True)
        df = self.convert_queue_to_df(short_queue)
        return df
    
    def get_long_queue_df(self):
        long_queue = self.get_long_queue()
        if long_queue is None:
            return None
        # initialize an empty dataframe
        # df = pd.DataFrame()
        # iterate through the long queue and append each element to the dataframe
        # len_long_queue = self.get_long_queue_length()
        # t0 = time.time()
        # for data_time_tuple in long_queue:
        #     parsed_dict = self.parse_radar_data(data_queue_element=data_time_tuple)
        #     if parsed_dict is None:
        #         continue
        #     df = df.append(parsed_dict, ignore_index=True)
        df = self.convert_queue_to_df(long_queue)
        return df
    
    def convert_queue_to_df(self, queue):
        if queue is None:
            return None
        # initialize an empty dataframe
        df = pd.DataFrame()
        # iterate through the queue and append each element to the dataframe
        len_queue = len(queue)
        t0 = time.time()
        list_of_tuples = []
        for data_time_tuple in queue:
            #####
            # parsed_dict = self.parse_radar_data(data_queue_element=data_time_tuple)
            # if parsed_dict is None:
            #     continue
            # df = pd.concat([df, pd.DataFrame([parsed_dict])], ignore_index=True)
            #####
            parsed_tuple = self.parse_radar_data(data_queue_element=data_time_tuple)
            if parsed_tuple is None:
                continue
            list_of_tuples.append(parsed_tuple)
        df = pd.DataFrame(
            list_of_tuples,
            columns = [
                'target1_x',
                'target1_y',
                'target1_speed',
                'target1_distance_res',
                'target2_x',
                'target2_y',
                'target2_speed',
                'target2_distance_res',
                'target3_x',
                'target3_y',
                'target3_speed',
                'target3_distance_res',
                'timestamp'
                ]
            )

        # try:
        #     print(f'parsing short queue took {time.time() - t0} seconds for {len_queue} elements, avg time per element: {(time.time() - t0) / len_queue} seconds')
        # except Exception:
        #     pass

        return df



    def get_short_queue_length(self):
        with self.short_queue_lock:
            return len(self.short_data_queue)
        
    def get_long_queue_length(self):
        with self.long_queue_lock:
            return len(self.long_data_queue)
        
    def clear_short_queue(self):
        with self.short_queue_lock:
            self.short_data_queue.clear()

    def clear_long_queue(self):
        with self.long_queue_lock:
            self.long_data_queue.clear()

    def clear_all_queues(self):
        self.clear_short_queue()
        self.clear_long_queue()

    def stop_running(self):
        # stops the run whether it is threaded or not
        with self.running_lock:
            self.running = False
        if self.thread is not None:
            try:
                if self.thread.is_alive():
                    self.thread.join()
                    self.thread = None
            except Exception as e:
                print(f'problem accessing the thread to stop it, error: {e}')

    def run_remote_sensor_thread(self, force_restart=False, loop_hold_time=0.5, daemon=True):
        # check if thread is already running
        if self.thread is not None:
            if self.thread.is_alive():
                if force_restart:
                    self.stop_thread()
                else:
                    return
        # else, start the thread
        self.thread = Thread(target=self.run_remote_sensor, args=(loop_hold_time,), daemon=daemon)
        self.thread.start()

    def parse_radar_data(self, data_queue_element=None, radar_data=None, radar_timestamp=None):
        '''
        A convenience method to parse the radar data into a @@@@@@@@@@@@@@@@@@@@@dictionary of target values.
        '''
        if data_queue_element is None and (radar_data is None or radar_timestamp is None):
            raise ValueError('Either data_queue_element or both radar_data and radar_timestamp must be provided')
        if data_queue_element is not None:
            # use it
            timestamp, radar_data = data_queue_element
        # target1_x, target1_y, target1_speed, target1_distance_res, \
        # target2_x, target2_y, target2_speed, target2_distance_res, \
        # target3_x, target3_y, target3_speed, target3_distance_res \
        #     = all_target_values
        all_target_values = read_radar_data(radar_data)

        
        if all_target_values is None:
            return None
        #####
        # radar_sample_dict = {
        #     'target1_x': all_target_values[0],
        #     'target1_y': all_target_values[1],
        #     'target1_speed': all_target_values[2],
        #     'target1_distance_res': all_target_values[3],
        #     'target2_x': all_target_values[4],
        #     'target2_y': all_target_values[5],
        #     'target2_speed': all_target_values[6],
        #     'target2_distance_res': all_target_values[7],
        #     'target3_x': all_target_values[8],
        #     'target3_y': all_target_values[9],
        #     'target3_speed': all_target_values[10],
        #     'target3_distance_res': all_target_values[11],
        #     'timestamp': timestamp,
        # }
        # return radar_sample_dict
        #####
        return all_target_values + (timestamp,)

    # wrap time_since_last_alive
    def time_since_last_alive(self):
        return self.client.time_since_last_alive()


                
    # Function to deserialize the data
    def deserialize_data(self, serialized_data, receive_timestamp):
        # Define the format string for a single tuple (timestamp, data)
        tuple_format = 'd30s'
        # Calculate the number of elements in the deque
        # Each element is 38 bytes long (8 bytes for double + 30 bytes for string)
        element_size = struct.calcsize(tuple_format)
        # print(f'element_size: {element_size}')
        total_size = len(serialized_data)
        # print(f'total_size: {total_size}')
        
        # Subtract the size of the final timestamp (8 bytes for double)
        n = (total_size - struct.calcsize('d')) // element_size
        # print(f'n: {n}')
        # print(f"another calculation: {1.0*(total_size - struct.calcsize('d')) / element_size}")
        
        # Define the format string for the entire deque + the final timestamp
        format_string = f'={tuple_format * n}d'
        # print(f'format_string: {format_string}, len(format_string): {struct.calcsize(format_string)}')
        
        # Unpack the data
        # print(f'len(data): {len(serialized_data)}, len(format_string): {struct.calcsize(format_string)}')
        unpacked_data = struct.unpack(format_string, serialized_data)
        
        # # Extract the deque elements and the final timestamp
        # data_deque = deque()
        
        final_timestamp = unpacked_data[-1] # timestamp from the server marking end of transmission

        timestamp_additive_offset = receive_timestamp - final_timestamp # offset to add to each timestamp to get the correct time

        data_and_timestamps_list = []
        for i in range(n):
            timestamp = unpacked_data[i * 2] + timestamp_additive_offset
            data = unpacked_data[i * 2 + 1].rstrip(b'\x00')  # Remove any padding null bytes
            # data_deque.append((timestamp, data))
            data_and_timestamps_list.append((timestamp, data))

        
        
        # return data_deque, final_timestamp + timestamp_additive_offset
        return data_and_timestamps_list, final_timestamp + timestamp_additive_offset
