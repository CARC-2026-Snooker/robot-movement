from enum import Enum
from smbus2 import SMBus

# Bit computation
def LowByte(number : int):
    return number & 0xFF
def HighByte(number : int):
    return number >> 24 & 0xFF

# Board Communication
PRIZM_MOTOR_ADDRESS = 5
PRIZM_SERVO_ADDRESS = 6
COMMUNICATION_PAUSE = 0.01 # Mimic the delay(10) of PRIZM's library
def ReadAddress():
    # Read the connected board address, please connect only one board at a time
    address = None
    
    with SMBus(1) as bus:
        for i in range(120):
            # PRIZM ignore
            if i == PRIZM_MOTOR_ADDRESS or i == PRIZM_SERVO_ADDRESS:
                continue
            
            try:
                bus.write_byte(i, 0)
            except:
                pass
            else:
                address = i

    return address

# Board Driver
class Wheel(Enum):
    FRONT = 1
    REAR = 2

# Illegal value checking
def ChannelCheck(channel : int):
    if channel != 1 and channel != 2:
        raise Exception("Channel out of range.")
def PowerCheck(power : int):
    if (power > 100 or power < -100) and power != 125:
        raise Exception("Power out of range.")
def SpeedCheck(speed : int):
    if speed > 720 or speed < -720:
        raise Exception("Speed out of range.")
def AbsSpeedCheck(degree : int):
    if degree > 720 or degree < 0:
        raise Exception("Speed out of range.") 
def InvertCheck(invert : int):
    if invert != 1 and invert != 0:
        raise Exception("Invalid invert value.")