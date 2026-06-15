from gpiozero import Button, DigitalOutputDevice
import time

button = Button(10)
output = DigitalOutputDevice(9)

print("Reading GPIO 10 and writing to GPIO 9... Press Ctrl+C to stop.")

try:
    while True:
        # button.value is 1 when pressed, 0 when released
        output.value = button.value
        print(button.value)
        # output.value = 1
        
        # A tiny sleep prevents the CPU from spiking to 100%
        time.sleep(0.001) 
        
except KeyboardInterrupt:
    print("\nScript stopped.")