import serial_protocol
import time
import pandas as pd


filename = 'radar_data.bin'
data_lines = []
# open file as binary and read all lines into a list
with open(filename, 'rb') as f:
    for line in f:
        line = line.strip()
        data_lines.append(line)
# initialize a pandas DataFrame to store the radar data
columns = [
    'timestamp',
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
    'target3_distance_res'
]
radar_data = pd.DataFrame(columns=columns)
counter = 0
for serial_port_line in data_lines:
    # print(repr(serial_port_line))
    all_target_values = serial_protocol.read_radar_data(serial_port_line)
        
    if all_target_values is None:  # line was corrupted and None was returned
        # continue
        # set all values to 0
        all_target_values = [0] * 12

    target1_x, target1_y, target1_speed, target1_distance_res, \
    target2_x, target2_y, target2_speed, target2_distance_res, \
    target3_x, target3_y, target3_speed, target3_distance_res \
        = all_target_values
    # add row to the DataFrame. df doesn't have an append method, so we concatenate the old df with a new one
    new_row = pd.DataFrame({
        # 'timestamp': [time.time()],
        'timestamp': [counter*0.09],
        'target1_x': [target1_x],
        'target1_y': [target1_y],
        'target1_speed': [target1_speed],
        'target1_distance_res': [target1_distance_res],
        'target2_x': [target2_x],
        'target2_y': [target2_y],
        'target2_speed': [target2_speed],
        'target2_distance_res': [target2_distance_res],
        'target3_x': [target3_x],
        'target3_y': [target3_y],
        'target3_speed': [target3_speed],
        'target3_distance_res': [target3_distance_res]
    })
    radar_data = pd.concat([radar_data, new_row], ignore_index=True)
    counter += 1

    # # Print the interpreted information for all targets
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
    # time.sleep(0.09)

print(radar_data)

# count how many target1_x values are greater than 0
target1_x_gt_0 = radar_data[radar_data['target1_x'] > 0]
print(f'Target 1 x-coordinate greater than 0: {len(target1_x_gt_0)}')

# # keep only the rows where target1_x is greater than 0
# radar_data = radar_data[radar_data['target1_x'] > 0]
# print(radar_data)

# add a column of 1 if target1_x is greater than 0, 0 otherwise
radar_data['target1_x_gt_0'] = radar_data['target1_x'] > 0

# add another column which is target1_x_gt_0 smoothed with a window of 22 samples
radar_data['target1_x_gt_0_smooth'] = radar_data['target1_x_gt_0'].rolling(window=22).mean()

# subtract the first timestamp from all timestamps
radar_data['timestamp'] -= radar_data['timestamp'].iloc[0]

# plot xy scatter plot of target1_x and target1_y
import matplotlib.pyplot as plt
# plt.scatter(radar_data['target1_x'], radar_data['target1_y'])
# make the color of the points correspond to the timestamp column
plt.scatter(radar_data['target1_x'], radar_data['target1_y'], c=radar_data['timestamp'])
plt.xlabel('x-coordinate (mm)')
plt.ylabel('y-coordinate (mm)')
plt.title('Target 1 x-y scatter plot')
plt.colorbar(label='Timestamp')
plt.show(block=False)
# # instead of showing the plot, save it to a file
# plt.savefig('target1_xy_scatter.png')
# await context.bot.send_photo(chat_id=update.effective_chat.id, photo=open('target1_xy_scatter.png', 'rb'))

# open another figure
plt.figure()
# plot target1_x_gt_0 and target1_x_gt_0_smooth vs timestamp
plt.plot(radar_data['timestamp'], radar_data['target1_x_gt_0'], label='target1_x_gt_0')
plt.plot(radar_data['timestamp'], radar_data['target1_x_gt_0_smooth'], label='target1_x_gt_0_smooth')
plt.xlabel('Time (s)')
plt.ylabel('Target 1 x-coordinate > 0')
plt.title('Target 1 x-coordinate > 0')
plt.legend()
plt.show(block=True)