# radar_watcher.py
# based on https://github.com/csRon/HLK-LD2450/

### see if we get anything from UART0
import serial
serial_port = '/dev/ttyS0'

def read_from_uart():
    # Open the serial port. Adjust the port name as necessary.
    ser = serial.Serial(serial_port, 256000, timeout=1)
    
    try:
        while True:
            if ser.in_waiting > 0:
                # Read a line from the serial interface
                line = ser.readline().decode('ascii').strip()
                print(f"Received: {line}")
    except KeyboardInterrupt:
        print("Exiting...")
    finally:
        ser.close()

read_from_uart()

### if that works, let's use it

import serial_protocol
import serial

# Open the serial port
ser = serial.Serial(serial_port, 256000, timeout=1)
