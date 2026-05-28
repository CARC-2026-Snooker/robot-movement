from smbus2 import SMBus
from utils import *

class MotorBoard():
    def __init__(self, address : int):
        self.address = address

    def SetAddress(self, new_address : int):
        with SMBus(1) as bus:
            bus.write_byte(self.address, 0x24)
            bus.write_byte(self.address, new_address)

    def ReadBatteryVoltage(self):
        with SMBus(1) as bus:
            bus.write_byte(self.address, 0x53)
            byte_1 = bus.read_byte(self.address)
            byte_2 = bus.read_byte(self.address)
        return byte_1 * 256 + byte_2

    def SetMotorPower(self, wheel : Wheel, power : int):
        PowerCheck(power)

        command = 0x40 + wheel - 1
        with SMBus(1) as bus:
            bus.write_byte(self.address, command)
            bus.write_byte(self.address, power)
    def SetMotorPowers(address : int, power_1 : int, power_2 : int):
        PowerCheck(power_1)
        PowerCheck(power_2)

        with SMBus(1) as bus:
            bus.write_byte(address, 0x42)
            bus.write_byte(address, power_1)
            bus.write_byte(address, power_2)

    def SetMotorSpeed(address : int, wheel : Wheel, speed : int):
        SpeedCheck(speed)

        command = 0x43 + wheel - 1
        with SMBus(1) as bus:
            bus.write_byte(address, command)
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

    def SetMotorTarget(address : int, wheel : int, speed : int, target : int):
        AbsSpeedCheck(speed)

        command = 0x46 + wheel - 1
        with SMBus(1) as bus:
            bus.write_byte(address, command)
            bus.write_byte(address, HighByte(speed))
            bus.write_byte(address, LowByte(speed))
            bus.write_byte(address, target)
            bus.write_byte(address, target >> 8)
            bus.write_byte(address, target >> 16)
            bus.write_byte(address, target >> 24)
    def SetMotorTargets(address : int, speed_1 : int, target_1 : int, speed_2 : int, target_2 : int):
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

    def SetMotorDegree(address : int, wheel : int, speed : int, degree : int):
        AbsSpeedCheck(speed)

        command = 0x58 + wheel - 1
        with SMBus(1) as bus:
            bus.write_byte(address, command)
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

    def SetMotorInvert(address : int, wheel : int, invert : int):
        InvertCheck(invert)

        command = 0x51 + wheel - 1
        with SMBus(1) as bus:
            bus.write_byte(address, command)
            bus.write_byte(invert)

    def ReadMotorBusy(address : int, wheel : Wheel):
        # 1 = busy, 0 = target reached
        command = 0x4F + wheel - 1
        with SMBus(1) as bus:
            bus.write_byte(address, command)
            status = bus.read_byte(address)
        return status


# Test section
if __name__ == "__main__":
    left_driver = MotorBoard(1)
    right_driver = MotorBoard(2)

    print(left_driver.ReadBatteryVoltage())
    print(right_driver.ReadBatteryVoltage())