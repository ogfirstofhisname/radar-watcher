from server_hostname import server_hostname
# from upython_sensor_server import WifiSensorServer

# wss = WifiSensorServer(
#     hostname=server_hostname,
#     port=1704,
#     poll_wait_time=0.05,
#     queue_size=100,
#     uart_rx_pin=17,
#     uart_tx_pin=16
# )

from upython_sensor_server import WifiRadarServer
wrs = WifiRadarServer(
    hostname=server_hostname,
    port=1704,
    poll_wait_time=0.05,
    queue_size=100,
    uart_rx_pin=17,
    uart_tx_pin=16
)

wss.start_server()