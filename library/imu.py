from mpu6050 import mpu6050
import math
import os
import time

sensor = mpu6050(0x68)

print("Calibrating gyro bias...")
samples = []

for _ in range(500):
    samples.append(sensor.get_gyro_data()["z"])
    time.sleep(0.01)

gyro_z_bias = sum(samples) / len(samples)

print(f"Gyro Z bias = {gyro_z_bias:.3f} deg/s")
print("Starting...")
time.sleep(1)

heading = 0.0
last_time = time.time()

while True:

    now = time.time()
    dt = now - last_time
    last_time = now

    accel = sensor.get_accel_data()
    gyro = sensor.get_gyro_data()

    ax = accel["x"]
    ay = accel["y"]
    az = accel["z"]

    roll = math.degrees(math.atan2(ay, az))
    pitch = math.degrees(
        math.atan2(-ax, math.sqrt(ay * ay + az * az))
    )

    gyro_z = gyro["z"] - gyro_z_bias

    heading += gyro_z * dt
    heading %= 360

    if gyro_z > 5:
        state = "ROTATING LEFT"
    elif gyro_z < -5:
        state = "ROTATING RIGHT"
    else:
        state = "STATIONARY"

    if heading < 45 or heading >= 315:
        compass = "N"
    elif heading < 135:
        compass = "E"
    elif heading < 225:
        compass = "S"
    else:
        compass = "W"

    os.system("clear")

    print("=" * 60)
    print(" MPU6050 HEADING TESTER ")
    print("=" * 60)

    print()
    print(f"Heading : {heading:7.1f}°")
    print(f"Compass : {compass}")
    print(f"State   : {state}")

    print()
    print(f"Gyro Z  : {gyro_z:7.2f} deg/s")

    print()
    print(f"Roll    : {roll:7.1f}°")
    print(f"Pitch   : {pitch:7.1f}°")

    print()
    print("Compass Rose")
    print()
    print("        N")
    print("        |")
    print("W ------+------ E")
    print("        |")
    print("        S")

    print()
    print(f"Raw Accel:")
    print(f"  X={ax:7.2f}")
    print(f"  Y={ay:7.2f}")
    print(f"  Z={az:7.2f}")

    time.sleep(0.02)