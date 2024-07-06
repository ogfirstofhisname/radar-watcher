An implementation for a remote server for HLK-LD2450 human detection radar, and a client.

The remote sensor server is implemented in MicroPython for ESP32, and the client is implemented in Python for Linux/Windows.

The server-client system is designed to be used in a home automation or a home security system (these radars are very good for detecting human presence).

## The *hlkld2540_network_client* Package
The client package is a Python package that provides a client wrapper for the HLK-LD2450 radar sensor server, including high-level functions such as data recording and analysis.

## The *_hlkld2450_esp32_upython_server_fs* Subdirectory
This is not a python package but rather, a MicroPython project for the ESP32. It is meant to be copied/programmed into an ESP32 board running a MicroPython firmware (with minor adjustments like the WiFi SSID and password).

## Hardware
- HLK-LD2450 radar sensor
- ESP32 board or module, for example, ESP32 DevKitC + a power source (e.g. USB charger)
- An 04SR cable to connect the radar sensor to the ESP32 board, or some other makeshift cable