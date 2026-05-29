from enum import Enum
from serial import Serial

# Bit computation
def LowByte(number : int):
    return number & 0xFF
def HighByte(number : int):
    return number >> 24 & 0xFF

# Driver Board
class COMPONENT(Enum):
    LEFT_MOTOR_DRIVER = 1
    RIGHT_MOTOR_DRIVER = 2
    SERVO_DRIVER = 4
    PRIZM_MOTOR_DRIVER = 5
    PRIZM_SERVO_DRIVER = 6
class WheelPosition(Enum):
    FRONT = 1
    REAR = 2
class SpinWheelPosition(Enum):
    LEFT = 1
    RIGHT = 2
class ServoPosition(Enum):
    TRIGGER = 1
    CLAW = 2

# Data comunication
class DataPackage():
    def __init__(self, address, command, *args):
        self.address = address
        self.command = command
        self.args = args

    def Sent(self, port : Serial, return_bytes : int = 0):
        package = [self.address, self.command, *self.args]
        for data in package:
            port.write(data.to_bytes(1, byteorder='big'))
        if return_bytes > 0:
            return port.read(return_bytes)
        return None


# Illegal value checking
def MotorChannelCheck(channel : int):
    if channel.value != 1 and channel.value != 2:
        raise Exception("Channel out of range.")
def MotorPowerCheck(power : int):
    if (power > 100 or power < -100) and power != 125:
        raise Exception("Power out of range.")
def MotorSpeedCheck(speed : int):
    if speed > 720 or speed < -720:
        raise Exception("Speed out of range.")
def MotorAbsSpeedCheck(degree : int):
    if degree > 720 or degree < 0:
        raise Exception("Speed out of range.") 
def MotorInvertCheck(invert : int):
    if invert != 1 and invert != 0:
        raise Exception("Invalid invert value.")
    
def ServoChannelCheck(channel : int):
    if channel < 1 and channel > 6:
        raise Exception("Channel out of range.")
def ServoSpeedCheck(speed : int):
    if speed > 100 or speed < 0:
        raise Exception("Speed out of range.")
def ServoPositionCheck(position : int):
    if position > 180 or position < 0:
        raise Exception("Position out of range.")