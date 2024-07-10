from collections import deque
import time
import struct

# initialize a long deque
long_queue = deque(maxlen=1000000)

# fill the deque with tuples of float and 30 bytes
for i in range(1000000):
    time_and_data_tuple = (time.time(), b'x' * 30)
    long_queue.append(time_and_data_tuple)

# define a parser function for the 30 bytes of data
def parse_queue_element(time_and_data_tuple):
    # some efficient implementation here...
    parsed_dict = {
        'target1_x': 1.0,
        'target1_y': 2.0,
        'target1_speed': 3.0,
        'target1_distance_resolution': 4.0,
        'target2_x': 5.0,
        'target2_y': 6.0,
        'target2_speed': 7.0,
        'target2_distance_resolution': 8.0,
        'target3_x': 9.0,
        'target3_y': 10.0,
        'target3_speed': 11.0,
        'target3_distance_resolution': 12.0,
        'timestamp': time_and_data_tuple[0]
    }
    return parsed_dict


