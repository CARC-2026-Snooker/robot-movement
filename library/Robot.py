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
    # FL FR RL RR
    if direction == Direction.FRONT:
        return [-1, 1, -1, 1]
    elif direction == Direction.LEFT:
        return [1, 1, -1, -1]
    elif direction == Direction.BACK:
        return [1, -1, 1, -1]
    elif direction == Direction.RIGHT:
        return [-1, -1, 1, 1]
    raise Exception("Unknown direction.")
def MapRotationToWheel(rotation : Rotation):
    # FL FR RL RR
    if rotation == Rotation.LEFT:
        return [1, 1, 1, 1]
    elif rotation == Rotation.RIGHT:
        return [-1, -1, -1, -1]
    raise Exception("Unknown rotation.")

class Robot():
    def __init__(self, serial_port : str = "/dev/ttyUSB0", baudrate : int = 1000000):
        self.serial = Serial(serial_port, baudrate)

        self.left_wheel_driver = Driver(Component.LEFT_MOTOR_DRIVER, self.serial)
        self.right_wheel_driver = Driver(Component.RIGHT_MOTOR_DRIVER, self.serial)
        self.spin_wheel_driver = Driver(Component.PRIZM_MOTOR_DRIVER, self.serial)
        self.servo_driver = Driver(Component.SERVO_DRIVER, self.serial)

        # Waiting for serial to initialize
        sleep(2)

        # Battery Checking sequence
        battery_levels = self.ReadBattery()
        for driver in battery_levels.keys():
            if battery_levels[driver] < 11:
                print(f"WARNING LOW BATTERY ({battery_levels[driver]})")
        
        print("Finish initialization, ready for shooting.")

    def Move(self, power : int, direction : Direction):
        multiplier = MapDirectionToWheel(direction)
        self.left_wheel_driver.SetMotorPowers(power * multiplier[0], power * multiplier[2])
        self.right_wheel_driver.SetMotorPowers(power * multiplier[1], power * multiplier[3])
    def Break(self):
        self.left_wheel_driver.SetMotorPowers(125, 125)
        self.right_wheel_driver.SetMotorPowers(125, 125)
    def Rotate(self, power : int, rotation : Rotation):
        self.left_wheel_driver.ResetEncoders()
        self.right_wheel_driver.ResetEncoders()
        
        multiplier = MapRotationToWheel(rotation)
        self.left_wheel_driver.SetMotorPowers(power * multiplier[0], power * multiplier[2])
        self.right_wheel_driver.SetMotorPowers(power * multiplier[1], power * multiplier[3])

        degree = 0
        while degree < 90:
            degree = abs(self.left_wheel_driver.ReadEncoderDegrees(WheelChannel.FRONT))
        self.Break()

    def OpenClaw(self):
        self.servo_driver.SetServoPosition(ServoChannel.CLAW, 140)
    def CloseClaw(self):
        self.servo_driver.SetServoPosition(ServoChannel.CLAW, 25)
    def ReleaseTrigger(self):
        self.servo_driver.SetServoPosition(ServoChannel.TRIGGER, 90)
    def ResetTrigger(self):
        self.servo_driver.SetServoPosition(ServoChannel.TRIGGER, 150)

    def RevUpSpinWheelPower(self, power : int):
        spin_direction = [1, -1] # Counter clock wise for left, clock wise for right
        self.spin_wheel_driver.SetMotorPowers(power * spin_direction[0], power * spin_direction[1])
    def StopSpinWheelPower(self):
        self.RevUpSpinWheelPower(0)

    def RevUpSpinWheelSpeed(self, speed : int):
        spin_direction = [1, -1] # Counter clock wise for left, clock wise for right
        self.spin_wheel_driver.SetMotorSpeeds(speed * spin_direction[0], speed * spin_direction[1])
    def StopSpinWheelSpeed(self):
        self.RevUpSpinWheelSpeed(0)

    def ReadBattery(self):
        return {
            "Left Driver" : self.left_wheel_driver.ReadBatteryVoltage() / 100,
            "Right Driver" : self.right_wheel_driver.ReadBatteryVoltage() / 100,
            "Servo Driver" : self.servo_driver.ReadBatteryVoltage() / 100,
        }

    def Stop(self):
        self.serial.close()

# Test section
if __name__ == "__main__":
    robot = Robot()

    print(robot.ReadBattery())
    
    # robot.OpenClaw()
    # # robot.RevUpSpinWheelSpeed(180)
    # sleep(1)
    # robot.ReleaseTrigger()
    # sleep(5)
    # robot.ResetTrigger()
    # # robot.StopSpinWheelSpeed()
    # robot.CloseClaw()

    # robot.Move(20, Direction.LEFT)
    # sleep(2)
    # robot.Break()
    # sleep(2)

    # robot.Move(20, Direction.BACK)
    # sleep(2)
    # robot.Break()
    # sleep(2)

    # robot.Move(20, Direction.RIGHT)
    # sleep(2)
    # robot.Break()
    # sleep(2)

    # print(robot.spin_wheel_driver.ReadEncoderDegrees(SpinWheelChannel.LEFT))

    # robot.Rotate(10, Rotation.RIGHT)

    robot.Stop()