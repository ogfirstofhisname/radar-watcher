import socket, time


def main():
    pass
    # create a client with hostname 'watchdog0' and port 1704
    client = WifiClient('192.168.120.34', 1704)
    print('created client')
    # send an empty message to the server
    for _ in range(5):
        response = client.transact_with_server('bdallack')
        # expected response is 'I am alive'
        print(f'got response: {response}')
        time.sleep(2)
        # now send a nonempty message to the server
        response = client.transact_with_server('wallack')
        # expected response is 'hello wallack'
        print(f'got response: {response}')
        time.sleep(4)

class WifiClient():

    def __init__(self, hostname:str, port:int):
        self.server_hostname = hostname
        self.server_port = port
        self.client_setup()
    
    def client_setup(self):
        self.server_ip = self.get_ip_address(self.server_hostname)
        if self.server_ip is None:
            raise Exception('error, server ip not found, check host name and network status')
        # set timeout for socket operations
        socket.setdefaulttimeout(3)

    def get_ip_address(self, hostname):
        try:
            return socket.gethostbyname(hostname)
        except socket.gaierror:
            print("Invalid hostname. Please check the hostname and try again.")
            return None

    def wait(self):
        time.sleep(0.05)

    # def subscribe_ip(self):   # doesn't return anything
    #     client_message = 'subscribe ' + self.subscribe_password
    #     self.transact_with_server(client_message)
    #     # TODO establish a response for subscribe

    def transact_with_server(self, client_message:str, timeout=1):  # always returns strings. Socket is opened for transaction and closed after transaction
        # TODO add try-except and a retry loop with increasing waits until an exception is raised
        # TODO maybe add some kind of echo on server side
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            client_socket.settimeout(timeout)  # Set the timeout for the socket
            client_socket.connect((self.server_ip, self.server_port))
            self.wait()
            client_socket.send(client_message.encode())  # TODO implement timeout
            self.wait()

            data = b""
            while True:
                packet = client_socket.recv(256)  # TODO implement timeout
                if not packet: 
                    break
                data += packet
                self.wait()
            print(f'got raw data: {repr(data)}')
            string_data = data.decode()
        return string_data
    
if __name__ == '__main__':
    main()
