
# "serial" is a module that allows us to communicate with serial ports
import serial

# "subprocess" is a module that allows us to run shell commands
import subprocess

# "exist" is a function to check if a directory exists
from os.path import exists

import time


# Exception registration
class CannotOpenPort(Exception):
    "Raised when the specified serial port doesn't exist"

    def __init__(self, message="Cannot open port. Is microbit connected?"):
        self.message = message
    
    def __str__(self):
        return self.message


class Disconnected(Exception):
    "Raised when the microbit is disconnected"

    def __init__(self, message="Microbit disconnected."):
        self.message = message

    def __str__(self):
        return self.message


# Port to microbit
port = "/dev/cu.usbmodem14102" # Change if needed; use 'ls /dev/cu.*' and look for '/dev/cu.usbmodem'

# Baud rate
baud = 115200

# Check if port path exists
if not exists(port):
    # Cannot find port
    raise CannotOpenPort()

# Create serial connection
s = serial.Serial(port)

# Set baud rate
s.baudrate = baud

print("Writing...")
s.write(b"helloooooo")
print("Done writing")

try:
    # Loop forever or until error
    while True:

        # If the port somehow is changed, just in case
        if not exists(port):
            # Cannot find port
            raise CannotOpenPort()

        # Read data from serial port
        raw_data = s.readline()

        # Decode data from bytes to string
        data = raw_data.decode('utf-8')

        # Remove newline character
        data = ' '.join(data.split())

        # Print data
        print(f"Data: '{data}'")
        
        # If data is 'play'
        if data == "Play":
            print("Resuming playback...")
            
            # Get contents of resume_audio.applescript
            f = open("resume_audio.applescript", "r")

            # Read contents
            data = f.read()

            # Close file
            f.close()

            # Run applescript
            # This will run the script from "resume_audio.applescript"
            subprocess.call(['osascript', '-e', data])

            # When is data playing since there is a delay
            check = True
            while check:
                res = subprocess.run("pmset -g", capture_output=True, text=True, shell=True).stdout.rstrip()
                check = res.split("displaysleep         60")[1].split(" highstandbythreshold")[0].split("\n")[0][1:]

                if check:
                    # There is audio playing
                    check = False

                    # Send string to microbit to turn off LED
                    s.write(b"LED_off")


                #else:
                    # No playback
            print("Playback resumed.")

except KeyboardInterrupt:
    # If user presses Ctrl+C
    print("\nExiting...")

    # Close serial connection
    s.close()

    print("Exited.")

except OSError:
    # On error related to the operating system (Usually if microbit is unplugged)
    print("oserror")

    # Close serial connection
    s.close()

    # Disconnected
    raise Disconnected()

except serial.serialutil.SerialException:
    # If there is some other error related to the serial connection
    print("serial exception")

    # Close serial connection
    s.close()
    
    # Raise the error (Raise means stop code with exception)
    raise
