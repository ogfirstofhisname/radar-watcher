An implementation for a remote server for HLK-LD2450 human detection radar, and a client.

The remote sensor server is implemented in MicroPython for ESP32, and the client is implemented in Python for Linux/Windows.

The server-client system is designed to be used in a home automation or a home security system (these radars are very good for detecting human presence).

## The *hlkld2540_network_client* Package
The client package is a Python package that provides a client wrapper for the HLK-LD2450 radar sensor server, including high-level functions such as data recording and analysis.

Parsing the data from the server is based on the [HLK-LD2450 project.](https://github.com/csRon/HLK-LD2450).

## The *_hlkld2450_esp32_upython_server_fs* Subdirectory
This is not a python package but rather, a MicroPython project for the ESP32. It is meant to be copied/programmed into an ESP32 board running a MicroPython firmware (with minor adjustments like the WiFi SSID and password).

On-board parsing of the data (optional, not used in the server-client system) is based on the [HLK-LD2450 project.](https://github.com/csRon/HLK-LD2450), with adaptations for MicroPython.

## Hardware
- HLK-LD2450 radar sensor
- ESP32 board or module, for example, ESP32 DevKitC + a power source (e.g. USB charger)
- An 04SR cable to connect the radar sensor to the ESP32 board, or some other makeshift cable

# Hardware Installation
Under construction.

# Software Installation
Under construction.

# Firmware Installation
Firmware installation involves 3 steps:
1. Flashing the MicroPython firmware to the ESP32 board
2. Editing the server_hostname_cfg.py and wifi_logins.py files for your network
3. Copying the server files to the ESP32 board

## Flashing the MicroPython Firmware
### Downloading the Firmware
Micropython is a binary firmware image that operates a Python interpreter and a file system on the ESP32 module. The firmware can be downloaded from the [MicroPython website](https://micropython.org/download/?port=esp32). Be sure to select the version suitable for your ESP32 board. If you're not 100% sure, just try them out - the wrong firmware shouldn't damage the board.
### Using Esptool
Typically, the firmware is flashed to the ESP32 board using the esptool.py script.
1. Connect the ESP32 board to your computer using a USB cable and find the port it's connected to (in Windows: open Device Manager, look under Ports (COM & LPT)).
2. Open a terminal with Python installed and run the following command:
```pip install esptool```
As a sanity check, run: ```esptool.py -p COMX chip_id``` (replace COMX with the port number).
3. After installation, run:  
```esptool.py --chip esp32 --port COMX erase_flash```  
to erase the flash memory (replace COMX with the port number). If you're using a fancy ESP32-S3 module, use ```esp32s3``` instead of ```esp32```.
4. Finally, run:  
```esptool.py --chip esp32 --port COMX --baud 460800 write_flash -z 0x1000 <path_to_firmware>```  
to flash the firmware (replace COMX with the port number and <path_to_firmware> with the path to the firmware binary).  
Example:  
```esptool.py --chip esp32 --port com4 --baud 460800 write_flash -z 0x1000 esp32-20230426-v1.20.0.bin```  
If you're using a fancy ESP32-S3 module, use ```esp32s3``` instead of ```esp32```, and ```0``` instead of ```0x1000```.

You're done! The ESP32 board should now be running MicroPython and responsive to serial commands, and can be connected to via a serial terminal (e.g. PuTTY) or a MicroPython-compatible IDE (e.g. Thonny).

## Editing the server_hostname_cfg.py and wifi_logins.py Files
The server_hostname_cfg.py file holds the hostname alias the remote sensor server will be using - it should be unique to each server (if you'll be using more than one server in your network).  
The wifi_logins.py file holds the SSID and password of the WiFi network the server will be connecting to - it should be edited so that your ESP32 board can connect to your network.  
Edit both files before copying them to the ESP32 board.

## Copying the Server Files to the ESP32 Board
The server files should be copied to the ESP32 board using a tool like mpypack.  
1. Install mpypack by running:  
```pip install mpypack```
2. Navigate to the folder containing the server files (```cd _hlkld2450_esp32_upython_server_fs```) and run:  
```mpypack -p COMX sync```  (replace COMX with the port number)

### Installing the HLK-LD2450 Project
Unfortunately, the project isn't structured as a python package - so it needs to be installed manually by cloning the repository and copying serial_protocol.py into a serial_protocol subdirectory in venv/Lib/site-packages.  
The serial_protocol.py file should also be edited to remove the pyserial import dependency (it's not needed in this project).