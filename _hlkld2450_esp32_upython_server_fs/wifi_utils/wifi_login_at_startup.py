import network  # type: ignore
import time
import os

def parse_wifi_logins():
    try:
        from wifi_logins import wifi_logins
        return wifi_logins
    except ImportError:
        print('could not import wifi_logins from wifi_logins.py')
        return {}




def connect_to_wifi(hostname='ESP32_server'):
    # Initialize the WiFi interface
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    time.sleep_ms(100)
    # # read hostname string from a file hostname.txt, strip it and set it
    # try:
    #     with open('hostname.txt', 'r') as f:
    #         hostname = f.read().strip()
    #         wlan.config(dhcp_hostname=hostname)
    # except Exception:
    #     hostname = 'sensorhub0'
    #     wlan.config(dhcp_hostname=hostname)
    wlan.config(dhcp_hostname=hostname)

#     wlan.config(dhcp_hostname='sensorhub0')
    # Scan for available networks
    print('scanning for wireless networks...')
    networks = wlan.scan()
#     network.hostname('sensorhub0')
#     wlan.config(dhcp_hostname='sensorhub0')

    # Sort networks by signal strength (network[3])
    networks.sort(key=lambda x: x[3], reverse=True)

    # Load the SSID:password dictionary
    wifi_logins = parse_wifi_logins()

    # Try to connect to each network in order
    for net in networks:
        ssid = net[0].decode('utf-8')
        if ssid in wifi_logins:
            password = wifi_logins[ssid]
            print('Trying to connect to', ssid)
            wlan.connect(ssid, password)

            # Wait for it to connect
            for i in range(10):
                if wlan.isconnected():
                    print('Connected to', ssid)
#                     network.hostname('sensorhub0')
#                     wlan.config(dhcp_hostname='sensorhub0')

                    return True
                time.sleep(1)
            print('Failed to connect to', ssid)

    # If it gets here, it failed to connect to any network
    print('Failed to connect to any network')
    return False



