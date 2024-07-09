import socket, time
from threading import Lock

class WifiClient():
    def __init__(self, hostname:str, port:int):
        self.server_hostname = hostname
        self.server_port = port
        self.server_status_lock = Lock()
        self.server_ip_lock = Lock()
        self.last_alive_time_lock = Lock()
        self.client_setup()
    
    def client_setup(self):
        # create locks for server status, server ip, last_alive_time
        # self.server_status_lock = Lock()
        # self.server_ip_lock = Lock()
        # self.last_alive_time_lock = Lock()
        with self.last_alive_time_lock:
            self.last_alive_time = None
        ip = self._get_ip_address(self.server_hostname)
        if ip is not None:
            self._online()
            self._alive()
        else:
            self._offline()
        
        # set timeout for socket operations
        socket.setdefaulttimeout(3)  # TODO change to about 10 for normal use
        
    def _online(self):
        with self.server_status_lock:
            self.server_status = 'online'

    def _offline(self):
        with self.server_status_lock:
            self.server_status = 'offline'

    def _alive(self):
        with self.server_status_lock:
            self.last_alive_time = time.time()

    def is_online(self):
        with self.server_status_lock:
            return self.server_status == 'online'
        
    def time_since_last_alive(self):
        with self.last_alive_time_lock:
            lat = self.last_alive_time
        if lat is None:
            return None
        else:
            return time.time() - lat
        
        

    def was_alive_recently(self, timeout=10):
        with self.last_alive_time_lock:
            lat = self.last_alive_time
        if lat is None:
            return False
        else:
            return time.time() - lat < timeout

    def _get_ip_address(self, hostname):
        try:
            ip = socket.gethostbyname(hostname)
            with self.server_ip_lock:
                self.server_ip = ip
            self._online()
            return ip
        except socket.gaierror:
            print("Invalid hostname. Please check the hostname and try again.")
            self._offline()
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
        # TODO maybe add some kind of echo on server side
        success = False
        receive_timestamp = None
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
                if timeout is not None:
                    client_socket.settimeout(timeout)  # Set the timeout for the socket
                client_socket.connect((self.server_ip, self.server_port))
                print('connected to server')
                self._wait()
                client_socket.send(client_message.encode())  # TODO implement timeout
                print(f'sent message: {client_message}')
                self._wait()

                data = b""
                while True:
                    packet = client_socket.recv(256)  # TODO implement timeout
                    if not packet: 
                        break
                    data += packet
                    # print(f'got packet: {repr(packet)}')
                    self._wait()
                # print(f'got raw data: {repr(data)}')
                self._alive()
                self._online()
                success = True
                receive_timestamp = time.time()
        except socket.timeout:
            # response was not sent promptly. The server may be in some fault state, or simply busy.
            print('Socket timed out')
            data = b''
        except ConnectionRefusedError:
            # the server is not accepting connections, may be in some fault state.
            print('Connection refused')
            data = b''
            self._offline()
        # except ConnectionResetError:
        #     print('Connection reset')
        #     data = b''
        #     self._offline()
        # except ConnectionAbortedError:
        #     print('Connection aborted')
        #     data = b''
        #     self._offline()
        except Exception as e:
            print(f'An exception occurred: {e}')
            data = b''
            
        return success, data, receive_timestamp