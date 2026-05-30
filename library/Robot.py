from enum import Enum
from time import sleep
from serial import Serial
from Driver import *

class Direction(Enum):
    FRONT = 0
    LEFT = 1
    BACK = 2
    RIGHT = 3
class Rotation(Enum):
    LEFT = 0
    RIGHT = 1

def MapDirectionToWheel(direction : Direction):
    if direction == Direction.FRONT:
        return [-1, -1, 1, 1]
    elif direction == Direction.LEFT:
        return [1, -1, 1, -1]
    elif direction == Direction.BACK:
        return [1, 1, -1, -1]
    elif direction == Direction.RIGHT:
        return [-1, 1, -1, 1]
    raise Exception("Unknown direction.")
def MapRotationToWheel(rotation : Rotation):
    if rotation == Direction.LEFT:
        return [1, 1, 1, 1]
    elif rotation == Direction.RIGHT:
        return [-1, -1, -1, -1]
    raise Exception("Unknown rotation.")

class Robot():
    def __init__(self, serial_port : str = "/dev/ttyUSB0", baudrate : int = 1000000):
        self.serial = Serial(serial_port, baudrate)

        self.left_wheel_driver = Driver(Component.LEFT_MOTOR_DRIVER, self.serial)
        self.right_wheel_driver = Driver(Component.RIGHT_MOTOR_DRIVER, self.serial)
        self.spin_wheel_driver = Driver(Component.PRIZM_MOTOR_DRIVER, self.serial)
        self.servo_driver = Driver(Component.PRIZM_SERVO_DRIVER, self.serial)

    def Move(self, power : int, direction : Direction):
        multiplier = MapDirectionToWheel(direction)
        self.left_wheel_driver.SetMotorPowers(power * multiplier[0], power * multiplier[1])
        self.right_wheel_driver.SetMotorPowers(power * multiplier[1], power * multiplier[2])
    def Break(self):
        self.left_wheel_driver.SetMotorPowers(125, 125)
        self.right_wheel_driver.SetMotorPowers(125, 125)
    def Rotate(self):
        pass

    def OpenClaw(self):
        servo_driver.SetServoPosition(ServoChannel.CLAW, 20)
    def CloseClaw(self):
        servo_driver.SetServoPosition(ServoChannel.CLAW, 140)
    def ReleaseTrigger(self):
        servo_driver.SetServoPosition(ServoChannel.TRIGGER, 150)
    def ResetTrigger(self):
        servo_driver.SetServoPosition(ServoChannel.TRIGGER, 90)

    def RevUpSpinWheel(self, power : int):
        spin_direction = [-1, 1] # Counter clock wise for left, clock wise for right
        spin_wheel_driver.SetMotorPowers(power * spin_direction[0], power * spin_direction[1])
    def StopSpinWheel(self):
        self.RevUpSpinWheel(0)

    def Stop(self):
        self.serial.close()

# Test section
if __name__ == "__main__":
    constant_speed = 10
    move_time = 1

    robot = Robot()
    robot.Move(constant_speed, Direction.FRONT)
    sleep(move_time)
    robot.Move(constant_speed, Direction.LEFT)
    sleep(move_time)
    robot.Move(constant_speed, Direction.BACK)
    sleep(move_time)
    robot.Move(constant_speed, Direction.RIGHT)
    sleep(move_time)
    robot.Break()

    robot.OpenClaw()
    sleep(move_time)
    robot.CloseClaw()
    sleep(move_time)

    robot.ReleaseTrigger()
    sleep(move_time)
    robot.ResetTrigger()
    sleep(move_time)

    robot.RevUpSpinWheel(20)
    sleep(move_time)
    robot.StopSpinWheel()
    sleep(move_time)

    robot.Stop()