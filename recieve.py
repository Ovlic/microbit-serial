
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


def playback_check():
    res = subprocess.run("pmset -g", capture_output=True, text=True, shell=True).stdout.rstrip()
    check_isplaying = res.split("displaysleep         60")[1].split(" highstandbythreshold")[0].split("\n")[0][1:]
    
    if check_isplaying:
        return True
    else:
        return False

    

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
        if data == "Button P0 Press" or "Button P0 Press" in data:

            # Check if playback is paused or not
            play_check = playback_check()

            print("Resuming Playback...") if play_check != True else print("Pausing Playback...")
            
            # Get contents of resume_audio.applescript
            f = open("resume_audio.applescript", "r")

            # Read contents
            data = f.read()

            # Close file
            f.close()

            # Run applescript
            # This will run the script from "resume_audio.applescript"
            subprocess.call(['osascript', '-e', data])

            # When is data playing since there is a delay in resuming audio to it actually playing
            check = True

            # Loop until check is false
            while check:

                # Call function to check for change in playback
                check_isplaying = playback_check()

                # print(f"check_isplaying: '{check_isplaying}'")

                # If audio was paused
                if play_check == False:
                    # If audio is playing right now
                    if check_isplaying:
                        print("Audio is playing")
                        # There is audio playing
                        check = False

                        # Send string to microbit to turn off LED
                        s.write(b"LED_off")
                    
                    # Delay to not spam the system
                    time.sleep(0.25)

                # If audio was playing
                elif play_check == True:
                    # If audio is paused right now
                    if not check_isplaying:
                        print("Audio is paused")
                        # There is audio playing
                        check = False

                        s.write(b"LED_off")



            #print("Playback resumed.") if play_check == True else print("Playback paused.")

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

