import socket, time
from hldld2450_network_client import WifiClient

def main():
    # create a client with hostname 'watchdog0' and port 1704
    client = WifiClient('192.168.120.34', 1704)
    print('created client')
    # send an empty message to the server
    for _ in range(5):
        success, response = client.transact_with_server('bdallack')
        # expected response is 'I am alive'
        print(f'success: {success}, response: {response}')
        time.sleep(2)
        # now send a nonempty message to the server
        success, response = client.transact_with_server('wallack')
        # expected response is 'hello wallack'
        print(f'success: {success}, response: {response}')
        time.sleep(4)

    
if __name__ == '__main__':
    main()
