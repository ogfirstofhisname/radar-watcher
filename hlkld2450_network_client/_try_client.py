import time, os
from hlkld2450 import HLKLD2450RemoteSensor
from serial_protocol.serial_protocol import read_radar_data
os.system('cls')



radar0 = HLKLD2450RemoteSensor(
    hostname = 'LD2450_server_0',
    port = 1704,
    len_short_queue=1000,
    len_long_queue=100000
)

radar1 = HLKLD2450RemoteSensor(
    hostname = 'LD2450_server_1',
    port = 1704,
    len_short_queue=1000,
    len_long_queue=100000
)

radar2 = HLKLD2450RemoteSensor(
    hostname = 'LD2450_server_2',
    port = 1704,
    len_short_queue=1000,
    len_long_queue=100000
)

radar3 = HLKLD2450RemoteSensor(
    hostname = 'LD2450_server_3',
    port = 1704,
    len_short_queue=1000,
    len_long_queue=100000
)

radars = [radar0, radar1, radar2, radar3]

# # check if the radar's client is initialized
# print(f'radar0 IP: {radar0.client.get_ip()}')

# print the ip of all radars
for radar in radars:
    print(f'{radar.name} IP: {radar.client.get_ip()}', end=', ')
print()

# run radar0
radar0.run_remote_sensor_thread()

# in a loop, print the time since last alive and fps, get the df and print the length of the long queue
while True:
    time.sleep(3)
    time_since_last_alive = radar0.time_since_last_alive()
    fps = radar0.get_fps()
    df = radar0.get_long_queue_df()
    long_queue_len = len(df)
    print(f'time_since_last_alive: {time_since_last_alive}, fps: {fps}, long_queue_len: {long_queue_len}')
    # print(df.head())

exit()

# check if the radar's client is online
print(f'radar0 client online: {radar0.client.check_if_online()}')

# check 3 more times
for i in range(3):
    time.sleep(1)
    print(f'radar0 client online: {radar0.client.check_if_online()}')

# start thread
radar0.run_remote_sensor_thread()

# wait 20 seconds and get df, while printing fps, queue lengths and time since last alive
for i in range(5):
    fps = radar0.get_fps()
    short_queue_len = radar0.get_short_queue_length()
    long_queue_len = radar0.get_long_queue_length()
    time_since_last_alive = radar0.client.time_since_last_alive()
    print(f'fps: {fps}, short_queue_len: {short_queue_len}, long_queue_len: {long_queue_len}, time_since_last_alive: {time_since_last_alive}')
    time.sleep(4)
df = radar0.get_long_queue_df()
print(df)

exit()

# radar0.run_remote_sensor_thread()
# radar1.run_remote_sensor_thread()
# radar2.run_remote_sensor_thread()
while True:
    time.sleep(1.1)
    # radar0.connect_and_update()
    radar0.client.check_if_online()
    t_r0 = radar0.client.time_since_last_alive()
    # radar1.client.check_if_online()
    # t_r1 = radar1.client.time_since_last_alive()
    # radar2.client.check_if_online()
    # t_r2 = radar2.client.time_since_last_alive()
    if t_r0 is not None:
        # round to 2 decimal places
        t_r0 = round(t_r0, 2)
        print(f'radar0: {t_r0}')
    # if t_r1 is not None:
    #     t_r1 = round(t_r1, 2)
    # if t_r2 is not None:
    #     t_r2 = round(t_r2, 2)
    # print(f'radar0: {t_r0}, radar1: {t_r1}, radar2: {t_r2}')
# radar.run_remote_sensor_thread()
# time.sleep(20)
# exit()

