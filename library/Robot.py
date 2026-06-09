import math
from enum import Enum
from time import sleep
from serial import Serial
from Driver import *

class Robot():
    def __init__(self, serial_port : str = "/dev/motor_controller", baudrate : int = 1000000):
        self.serial = Serial(serial_port, baudrate)

        self.left_wheel_driver = Driver(Component.LEFT_MOTOR_DRIVER, self.serial)
        self.right_wheel_driver = Driver(Component.RIGHT_MOTOR_DRIVER, self.serial)
        self.spin_wheel_driver = Driver(Component.PRIZM_MOTOR_DRIVER, self.serial)
        self.servo_driver = Driver(Component.SERVO_DRIVER, self.serial)

        self.wheel_radius = 10.225 # cm
        self.length = 27.753 # cm
        self.width = 27.753 # cm

        # Waiting for serial to initialize
        sleep(2)

        # Battery Checking sequence
        battery_levels = self.ReadBattery()
        for driver in battery_levels.keys():
            if battery_levels[driver] < 11:
                print(f"WARNING LOW BATTERY ({battery_levels[driver]})")
        
        print("Finish initialization, ready for shooting.")

    def OmniMovement(self, vX : int, vY : int, vR : int):
        """
        vX: Velocity in x axis (range from -720 to 720)\n
        vY: Velocity in y axis (range from -720 to 720)\n
        vR: Angular velocity (range from -720 to 720)\n

        All velocity parameters have unit of degree per second.
        """
        fl = -( vY + vX + vR)
        fr = -(-vY + vX + vR)
        rl = -( vY - vX + vR)
        rr = -(-vY - vX + vR)

        max_val = max(abs(fl), abs(fr), abs(rl), abs(rr))
        if max_val > 720:
            fl /= max_val
            fr /= max_val
            rl /= max_val
            rr /= max_val

        fl = round(fl)
        fr = round(fr)
        rl = round(rl)
        rr = round(rr)

        self.left_wheel_driver.SetMotorSpeeds(fl, rl)
        self.right_wheel_driver.SetMotorSpeeds(fr, rr)
    def Move(self, movement_speed : int, movement_degree : int, rotation_speed : int):
        #       0
        # 270   ^    90
        #      180
        vX = movement_speed * math.sin(math.radians(movement_degree)) # need to convert to radians before use for sin/cos
        vY = movement_speed * math.cos(math.radians(movement_degree))
        self.OmniMovement(vX, vY, rotation_speed)
    def Break(self):
        self.left_wheel_driver.SetMotorPowers(125, 125)
        self.right_wheel_driver.SetMotorPowers(125, 125)
    def Rotate(self, speed : int, degree : int):
        """
        For stationary rotating.
        """
        # multiplier = MapRotationToWheel(rotation)

        # fl_count = self.left_wheel_driver.ReadEncoderCount(WheelChannel.FRONT)
        # fr_count = self.right_wheel_driver.ReadEncoderCount(WheelChannel.FRONT)
        # rl_count = self.left_wheel_driver.ReadEncoderCount(WheelChannel.REAR)
        # rr_count = self.right_wheel_driver.ReadEncoderCount(WheelChannel.REAR)

        # self.left_wheel_driver.SetMotorTargets(speed, 1320 * multiplier[0], speed, 1320 * multiplier[2])
        # self.right_wheel_driver.SetMotorTargets(speed, 1320 * multiplier[1], speed, 1320 * multiplier[3])
        # while (self.left_wheel_driver.ReadMotorBusy(WheelChannel.FRONT) or 
        #        self.left_wheel_driver.ReadMotorBusy(WheelChannel.REAR) or 
        #        self.right_wheel_driver.ReadMotorBusy(WheelChannel.FRONT) or 
        #        self.right_wheel_driver.ReadMotorBusy(WheelChannel.REAR)):
        #     sleep(0.1)

        target = -15 * degree
        self.left_wheel_driver.SetMotorTargets(speed, target, speed, target)
        self.right_wheel_driver.SetMotorTargets(speed, target, speed, target)

        # Block all code execution until the robot finish rotating
        sleep(0.1)
        while self.left_wheel_driver.ReadMotorBusy(WheelChannel.FRONT):
            sleep(0.1)
    def RotateStack(self, speed, degree):
        delta = -15 * degree

        lf = self.left_wheel_driver.ReadEncoderCount(WheelChannel.FRONT)
        lr = self.left_wheel_driver.ReadEncoderCount(WheelChannel.REAR)
        rf = self.right_wheel_driver.ReadEncoderCount(WheelChannel.FRONT)
        rr = self.right_wheel_driver.ReadEncoderCount(WheelChannel.REAR)

        self.left_wheel_driver.SetMotorTargets(
            speed, lf + delta,
            speed, lr + delta
        )

        self.right_wheel_driver.SetMotorTargets(
            speed, rf + delta,
            speed, rr + delta
        )

        sleep(0.1)
        while (
            self.left_wheel_driver.ReadMotorBusy(WheelChannel.FRONT) or
            self.left_wheel_driver.ReadMotorBusy(WheelChannel.REAR) or
            self.right_wheel_driver.ReadMotorBusy(WheelChannel.FRONT) or
            self.right_wheel_driver.ReadMotorBusy(WheelChannel.REAR)
        ):
            sleep(0.1)
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

    # robot.Move(400, 0, 20)
    # # robot.OmniMovement(0, 100, 0)
    # # robot.RevUpSpinWheelPower(40)
    # sleep(3)
    # # robot.ReleaseTrigger()
    # # sleep(2)
    # # robot.ResetTrigger()
    # # robot.StopSpinWheelPower()
    # robot.Break()
    # sleep(2)

    # robot.OpenClaw()
    # sleep(1.9)
    # robot.CloseClaw()

    # robot.RotateStack(100, 180)
    # # robot.RotateStack(100, 90)
    # # robot.RotateStack(100, 90)
    # sleep(2)
    # # robot.Move(-100, 0, 150)
    # robot.Break()
    # sleep(2)
    # # robot.RotateStack(100, -90)
    # # robot.RotateStack(100, -90)
    # robot.RotateStack(100, 90)
    # # robot.Move(20, 45)
    # # robot.OmniMovement(0, 10, )
    # sleep(2)
    robot.Break()

    robot.Stop()