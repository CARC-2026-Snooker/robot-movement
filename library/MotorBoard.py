from smbus2 import SMBus
import time
from utils import *

PRIZM_ADDRESS = 5
COMMUNICATION_PAUSE = 0.01 # Mimic the delay(10) of PRIZM's library

def ReadAddress():
    address = None
    
    with SMBus(1) as bus:
        for i in range(120):
            # PRIZM ignore
            if i == PRIZM_ADDRESS:
                continue
            
            try:
                bus.write_byte(i, 0)
            except:
                pass
            else:
                address = i

    return address
def SetAddress(new_address : int):
    oldAddress = ReadAddress()

    with SMBus(1) as bus:
        bus.write_byte(oldAddress, 0x24)
        bus.write_byte(oldAddress, new_address)

def ReadBatteryVoltage(address : int):
    with SMBus(1) as bus:
        bus.write_byte(address, 0x53)
        byte_1 = bus.read_byte(address)
        byte_2 = bus.read_byte(address)
    return byte_1 * 256 + byte_2

def SetMotorPower(address : int, channel : int, power : int):
    ChannelCheck(channel)
    PowerCheck(power)

    channel = 0x40 + channel - 1
    with SMBus(1) as bus:
        bus.write_byte(address, channel)
        bus.write_byte(address, power)
def SetMotorPowers(address : int, power_1 : int, power_2 : int):
    PowerCheck(power_1)
    PowerCheck(power_2)

    with SMBus(1) as bus:
        bus.write_byte(address, 0x42)
        bus.write_byte(address, power_1)
        bus.write_byte(address, power_2)

def SetMotorSpeed(address : int, channel : int, speed : int):
    ChannelCheck(channel)
    SpeedCheck(speed)

    channel = 0x43 + channel - 1
    with SMBus(1) as bus:
        bus.write_byte(address, channel)
        bus.write_byte(address, HighByte(speed))
        bus.write_byte(address, LowByte(speed))
def SetMotorSpeeds(address : int, speed_1 : int, speed_2 : int):
    SpeedCheck(speed_1)
    SpeedCheck(speed_2)
    
    with SMBus(1) as bus:
        bus.write_byte(address, 0x45)
        bus.write_byte(address, HighByte(speed_1))
        bus.write_byte(address, LowByte(speed_1))
        bus.write_byte(address, HighByte(speed_2))
        bus.write_byte(address, LowByte(speed_2))

def SetMotorTarget(address : int, channel : int, speed : int, target : int):
    ChannelCheck(channel)
    AbsSpeedCheck(speed)

    channel = 0x46 + channel - 1
    with SMBus(1) as bus:
        bus.write_byte(address, channel)
        bus.write_byte(address, HighByte(speed))
        bus.write_byte(address, LowByte(speed))
        bus.write_byte(address, target)
        bus.write_byte(address, target >> 8)
        bus.write_byte(address, target >> 16)
        bus.write_byte(address, target >> 24)
def SetMotorTarget(address : int, speed_1 : int, target_1 : int, speed_2 : int, target_2 : int):
    AbsSpeedCheck(speed_1)
    AbsSpeedCheck(speed_2)

    channel = 0x46 + channel - 1
    with SMBus(1) as bus:
        bus.write_byte(address, 0x48)

        bus.write_byte(address, HighByte(speed_1))
        bus.write_byte(address, LowByte(speed_1))
        bus.write_byte(address, target_1)
        bus.write_byte(address, target_1 >> 8)
        bus.write_byte(address, target_1 >> 16)
        bus.write_byte(address, target_1 >> 24)

        bus.write_byte(address, HighByte(speed_2))
        bus.write_byte(address, LowByte(speed_2))
        bus.write_byte(address, target_2)
        bus.write_byte(address, target_2 >> 8)
        bus.write_byte(address, target_2 >> 16)
        bus.write_byte(address, target_2 >> 24)

def SetMotorDegree(address : int, channel : int, speed : int, degree : int):
    ChannelCheck(channel)
    AbsSpeedCheck(speed)

    channel = 0x58 + channel - 1
    with SMBus(1) as bus:
        bus.write_byte(address, channel)
        bus.write_byte(address, HighByte(speed))
        bus.write_byte(address, LowByte(speed))
        bus.write_byte(address, degree)
        bus.write_byte(address, degree >> 8)
        bus.write_byte(address, degree >> 16)
        bus.write_byte(address, degree >> 24)
def SetMotorDegrees(address : int, speed_1 : int, degree_1 : int, speed_2 : int, degree_2 : int):
    AbsSpeedCheck(speed_1)
    AbsSpeedCheck(speed_2)

    with SMBus(1) as bus:
        bus.write_byte(address, 0x5A)

        bus.write_byte(address, HighByte(speed_1))
        bus.write_byte(address, LowByte(speed_1))
        bus.write_byte(address, degree_1)
        bus.write_byte(address, degree_1 >> 8)
        bus.write_byte(address, degree_1 >> 16)
        bus.write_byte(address, degree_1 >> 24)

        bus.write_byte(address, HighByte(speed_2))
        bus.write_byte(address, LowByte(speed_2))
        bus.write_byte(address, degree_2)
        bus.write_byte(address, degree_2 >> 8)
        bus.write_byte(address, degree_2 >> 16)
        bus.write_byte(address, degree_2 >> 24)

def SetMotorInvert(address : int, channel : int, invert : int):
    ChannelCheck(channel)
    InvertCheck(invert)

    channel = 0x51 + channel - 1
    with SMBus(1) as bus:
        bus.write_byte(address, channel)
        bus.write_byte(invert)

def ReadMotorBusy(address : int, channel : int):
    # 1 = busy, 0 = target reached

    ChannelCheck(channel)

    channel = 0x4F + channel - 1
    with SMBus(1) as bus:
        bus.write_byte(address, channel)
        status = bus.read_byte(address)
    return status
