try:
    from _hlkld2450_esp32_upython_server_fs.server_hostname_cfg import server_hostname
except ImportError:
    from server_hostname_cfg import server_hostname


from upython_sensor_server import WifiRadarServer
wrs = WifiRadarServer(
    hostname=server_hostname,
    port=1704,
    poll_wait_time=0,
    queue_size=340,  # about 30 seconds of buffer
    uart_rx_pin=16,
    uart_tx_pin=17
)

wrs.start_server()

