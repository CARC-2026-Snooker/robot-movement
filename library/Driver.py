from time import sleep
from enum import Enum
from serial import Serial
from utils import *

# Components and its positioning
class Component(Enum):
    LEFT_MOTOR_DRIVER = 1
    RIGHT_MOTOR_DRIVER = 2
    SERVO_DRIVER = 4
    PRIZM_MOTOR_DRIVER = 5
    PRIZM_SERVO_DRIVER = 6
class WheelChannel(Enum):
    FRONT = 1
    REAR = 2
class SpinWheelChannel(Enum):
    LEFT = 1
    RIGHT = 2
class ServoChannel(Enum):
    CLAW = 1
    TRIGGER = 2

# Illegal value checking helper functions
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


class Driver():
    def __init__(self, component : Component, port : Serial):
        self.address = component.value
        self.port = port

    def ReadBatteryVoltage(self):
        package = DataPackage(self.address, 0x53)
        data = package.Sent(self.port, 2)
        return data[0] * 256 + data[1]

    # =====================
    # Motor
    # =====================
    def SetMotorPower(self, wheel : WheelChannel | SpinWheelChannel, power : int):
        MotorPowerCheck(power)

        command = 0x40 + wheel.value - 1
        package = DataPackage(self.address, command, power)
        package.Sent(self.port)
    def SetMotorPowers(self, power_1 : int, power_2 : int):
        MotorPowerCheck(power_1)
        MotorPowerCheck(power_2)

        package = DataPackage(self.address, 0x42, power_1, power_2)
        package.Sent(self.port)

    def SetMotorSpeed(self, wheel : WheelChannel | SpinWheelChannel, speed : int):
        MotorSpeedCheck(speed)

        command = 0x43 + wheel.value - 1
        package = DataPackage(self.address, command, speed)
        package.Sent(self.port)
    def SetMotorSpeeds(self, speed_1 : int, speed_2 : int):
        MotorSpeedCheck(speed_1)
        MotorSpeedCheck(speed_2)
        
        package = DataPackage(self.address, 0x45, speed_1, speed_2)
        package.Sent(self.port)

    def SetMotorTarget(self, wheel : WheelChannel | SpinWheelChannel, speed : int, target : int):
        MotorAbsSpeedCheck(speed)

        command = 0x46 + wheel.value - 1
        arguments = [
            HighByte(speed),
            LowByte(speed),
            target & 0xFF,
            target >> 8 & 0xFF,
            target >> 16 & 0xFF,
            target >> 24 & 0xFF,
        ]
        package = DataPackage(self.address, command, *arguments)
        package.Sent(self.port)
    def SetMotorTargets(self, speed_1 : int, target_1 : int, speed_2 : int, target_2 : int):
        MotorAbsSpeedCheck(speed_1)
        MotorAbsSpeedCheck(speed_2)

        arguments_1 = [
            HighByte(speed_1),
            LowByte(speed_1),
            target_1 & 0xFF,
            target_1 >> 8 & 0xFF,
            target_1 >> 16 & 0xFF,
            target_1 >> 24 & 0xFF,
        ]
        arguments_2 = [
            HighByte(speed_2),
            LowByte(speed_2),
            target_2 & 0xFF,
            target_2 >> 8 & 0xFF,
            target_2 >> 16 & 0xFF,
            target_2 >> 24 & 0xFF,
        ]
        package = DataPackage(self.address, 0x48, *arguments_1.extend(arguments_2))
        package.Sent(self.port)

    def SetMotorDegree(self, wheel : WheelChannel | SpinWheelChannel, speed : int, degree : int):
        MotorAbsSpeedCheck(speed)

        command = 0x58 + wheel.value - 1
        arguments = [
            HighByte(speed),
            LowByte(speed),
            degree & 0xFF,
            degree >> 8 & 0xFF,
            degree >> 16 & 0xFF,
            degree >> 24 & 0xFF,
        ]
        package = DataPackage(self.address, command, arguments)
        package.Sent(self.port)
    def SetMotorDegrees(self, speed_1 : int, degree_1 : int, speed_2 : int, degree_2 : int):
        MotorAbsSpeedCheck(speed_1)
        MotorAbsSpeedCheck(speed_2)

        arguments_1 = [
            HighByte(speed_1),
            LowByte(speed_1),
            degree_1 & 0xFF,
            degree_1 >> 8 & 0xFF,
            degree_1 >> 16 & 0xFF,
            degree_1 >> 24 & 0xFF,
        ]
        arguments_2 = [
            HighByte(speed_2),
            LowByte(speed_2),
            degree_2 & 0xFF,
            degree_2 >> 8 & 0xFF,
            degree_2 >> 16 & 0xFF,
            degree_2 >> 24 & 0xFF,
        ]
        package = DataPackage(self.address, 0x5A, *arguments_1.extend(arguments_2))
        package.Sent(self.port)

    def SetMotorInvert(self, wheel : WheelChannel | SpinWheelChannel, invert : int):
        MotorInvertCheck(invert)

        command = 0x51 + wheel.value - 1
        package = DataPackage(self.address, command, invert)
        package.Sent(self.port)

    def ReadMotorBusy(self, wheel : WheelChannel | SpinWheelChannel):
        # 1 = busy, 0 = target reached
        command = 0x4F + wheel.value - 1
        package = DataPackage(self.address, command)
        return package.Sent(self.port, 1)

    # =====================
    # Servo
    # =====================
    def SetServoSpeed(self, servo : ServoChannel, servo_speed : int):
        ServoSpeedCheck(servo_speed)

        command = 0x28 + servo.value - 1
        package = DataPackage(self.address, command, servo_speed)
        package.Sent(self.port)
    def SetServoSpeeds(
            self,
            servo_speed_1 : int,
            servo_speed_2 : int,
            servo_speed_3 : int,
            servo_speed_4 : int,
            servo_speed_5 : int,
            servo_speed_6 : int
        ):
        ServoSpeedCheck(servo_speed_1)
        ServoSpeedCheck(servo_speed_2)
        ServoSpeedCheck(servo_speed_3)
        ServoSpeedCheck(servo_speed_4)
        ServoSpeedCheck(servo_speed_5)
        ServoSpeedCheck(servo_speed_6)

        package = DataPackage(
            self.address,
            0x2E,
            servo_speed_1,
            servo_speed_2,
            servo_speed_3,
            servo_speed_4,
            servo_speed_5,
            servo_speed_6
        )
        package.Sent()

    def SetServoPosition(self, servo : ServoChannel, servo_position : int):
        ServoPositionCheck(servo_position)

        command = 0x2F + servo.value - 1
        package = DataPackage(self.address, command, servo_position)
        package.Sent(self.port)
    def SetServoPositions(
            self,
            servo_position_1 : int,
            servo_position_2 : int,
            servo_position_3 : int,
            servo_position_4 : int,
            servo_position_5 : int,
            servo_position_6 : int
        ):
        ServoPositionCheck(servo_position_1)
        ServoPositionCheck(servo_position_2)
        ServoPositionCheck(servo_position_3)
        ServoPositionCheck(servo_position_4)
        ServoPositionCheck(servo_position_5)
        ServoPositionCheck(servo_position_6)

        package = DataPackage(
            self.address,
            0x35,
            servo_position_1,
            servo_position_2,
            servo_position_3,
            servo_position_4,
            servo_position_5,
            servo_position_6
        )
        package.Sent()

# Test section
if __name__ == "__main__":
    serial = Serial("/dev/ttyUSB0", baudrate=1000000, timeout=1)
    sleep(4)

    left_motor_driver = Driver(Component.LEFT_MOTOR_DRIVER, serial)
    right_motor_driver = Driver(Component.RIGHT_MOTOR_DRIVER, serial)
    servo_driver = Driver(Component.PRIZM_SERVO_DRIVER, serial)
    spin_wheel_driver = Driver(Component.PRIZM_MOTOR_DRIVER, serial)

    # print(left_motor_driver.ReadBatteryVoltage())
    # print(right_motor_driver.ReadBatteryVoltage())
    # print(servo_driver.ReadBatteryVoltage())
    # print(spin_wheel_driver.ReadBatteryVoltage())

    # spin_wheel_driver.SetMotorPower(SpinWheelChannel.LEFT, 100)
    left_motor_driver.SetMotorPower(WheelChannel.FRONT, 15)
    left_motor_driver.SetMotorPower(WheelChannel.REAR, 15)
    right_motor_driver.SetMotorPower(WheelChannel.FRONT, 15)
    right_motor_driver.SetMotorPower(WheelChannel.REAR, 15)

    # servo_driver.SetServoPosition(ServoChannel.CLAW, 20)
    # servo_driver.SetServoPosition(ServoChannel.CLAW, 140)

    # servo_driver.SetServoPosition(ServoChannel.TRIGGER, 150)
    sleep(1)
    # servo_driver.SetServoPosition(ServoChannel.TRIGGER, 90)
    
    print("sent")
    sleep(5)

    serial.close()
