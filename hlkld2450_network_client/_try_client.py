import socket, time
from hldld2450_network_client import WifiClient
from serial_protocol.serial_protocol import read_radar_data

def main():
    # create a client with hostname 'watchdog0' and port 1704
    client = WifiClient('LD2450_server_0', 1704)
    print('created client')
    clear_success = False
    while not clear_success:
        if client.is_online():
            clear_success, response, receive_timestamp = client.transact_with_server('clear')
            print(f'sent clear command, success: {clear_success}, response: {response}, receive_timestamp: {receive_timestamp}')
    # send an empty message to the server
    while True:
        if client.is_online():
            success, response, receive_timestamp = client.transact_with_server('get')
            print('got response')
            if not success:
                print('Server not responding, waiting and trying again...')
                time.sleep(1)
                continue
            # expected response is 'I am alive'
            # print(f'success: {success}, response: {response}')
            data_queue, final_timestamp = deserialize_data(response, receive_timestamp)
            print('data deserialized')
            for data_time_tuple in data_queue:
                # timestamp = unpacked_data[i * 2]
                # data = unpacked_data[i * 2 + 1].rstrip(b'\x00')  # Remove any padding null bytes
                # data_deque.append((timestamp, data))
                timestamp, data = data_time_tuple
                # print(f'timestamp: {timestamp}, data: {data}')
                all_target_values = read_radar_data(data)
                if all_target_values is None:
                    print('got None from read_radar_data')
                    continue
                target1_x, target1_y, target1_speed, target1_distance_res, \
                target2_x, target2_y, target2_speed, target2_distance_res, \
                target3_x, target3_y, target3_speed, target3_distance_res \
                    = all_target_values
                print(f'Target 1 y-coordinate: {target1_y} mm, timestamp: {timestamp}, final_timestamp: {final_timestamp}')
                # Print the interpreted information for all targets
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
            # print('data_queue:')
            # print(data_queue)
            # print(f'final_timestamp: {final_timestamp}')
            time.sleep(0.5)
            # # now send a nonempty message to the server
            # success, response = client.transact_with_server('wallack')
            # # expected response is 'hello wallack'
            # # print(f'success: {success}, response: {response}')
            # time.sleep(4)
        else:
            print('Server is offline, waiting and trying again...')
            time.sleep(1)
            client.client_setup()
            continue

    
import struct
from collections import deque

# Define the format string for a single tuple (timestamp, data)
tuple_format = 'd30s'

# Function to deserialize the data
def deserialize_data(serialized_data, receive_timestamp):
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
    
    # Extract the deque elements and the final timestamp
    data_deque = deque()
    
    final_timestamp = unpacked_data[-1] # timestamp from the server marking end of transmission

    timestamp_additive_offset = receive_timestamp - final_timestamp # offset to add to each timestamp to get the correct time

    for i in range(n):
        timestamp = unpacked_data[i * 2] + timestamp_additive_offset
        data = unpacked_data[i * 2 + 1].rstrip(b'\x00')  # Remove any padding null bytes
        data_deque.append((timestamp, data))

    
    
    return data_deque, final_timestamp + timestamp_additive_offset


if __name__ == '__main__':
    main()
