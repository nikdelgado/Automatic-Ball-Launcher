"""
Project: Automatic Dog Ball Launcher
Author: Nikolas Delgado
Description:
    This program uses a VL53L0X Time-of-Flight sensor to detect proximity
    and control two motors and a servo for a ball-triggering system.
    The motors operate based on a random power level and the servo
    releases the ball when the object is detected within range.
"""

import time
import random
import board
import busio
import pwmio
import digitalio
from adafruit_motor import servo
import adafruit_vl53l0x

# ------------------------------
# Initialization
# ------------------------------

# Enable VL53L0X sensor
sensor_enable = digitalio.DigitalInOut(board.GP2)
sensor_enable.direction = digitalio.Direction.OUTPUT
sensor_enable.value = True
time.sleep(1)  # Allow the sensor to power up

# Initialize I2C and VL53L0X sensor
try:
    i2c = busio.I2C(board.GP1, board.GP0)
    time.sleep(0.5)  # Ensure the I2C bus stabilizes
    vl53 = adafruit_vl53l0x.VL53L0X(i2c)
    time.sleep(0.5)
except Exception as e:
    raise

# Initialize motors (PWM for speed control)
motor1_pwm = pwmio.PWMOut(board.GP15, frequency=5000, duty_cycle=0)  # Motor 1 speed
motor2_pwm = pwmio.PWMOut(board.GP14, frequency=5000, duty_cycle=0)  # Motor 2 speed

# Initialize motor direction control pins
motor1_dir1 = digitalio.DigitalInOut(board.GP11)
motor1_dir2 = digitalio.DigitalInOut(board.GP12)
motor2_dir1 = digitalio.DigitalInOut(board.GP13)
motor2_dir2 = digitalio.DigitalInOut(board.GP10)

# Set motor direction pins as outputs
for pin in [motor1_dir1, motor1_dir2, motor2_dir1, motor2_dir2]:
    pin.direction = digitalio.Direction.OUTPUT

# Initialize servo
servo_pwm = pwmio.PWMOut(board.GP16, duty_cycle=2 ** 15, frequency=50)
ball_servo = servo.Servo(servo_pwm)

# Set initial servo position
ball_servo.angle = 90  # Closed position
time.sleep(0.5)

# ------------------------------
# Functions
# ------------------------------

def set_motor_direction():
    motor1_dir1.value = True
    motor1_dir2.value = False
    motor2_dir1.value = True
    motor2_dir2.value = False

def stop_motors():
    motor1_pwm.duty_cycle = 0
    motor2_pwm.duty_cycle = 0

# ------------------------------
# Main Loop
# ------------------------------

try:
    while True:
        # Check if an object is detected within range
        if vl53.range < 50:
            # Generate a random motor power level
            motor_power = random.randrange(40000, 64000, 2000)

            # Set motor direction and start motors
            set_motor_direction()
            motor1_pwm.duty_cycle = motor_power
            time.sleep(0.5)  # Allow motors to start up
            motor2_pwm.duty_cycle = motor_power
            time.sleep(2)  

            # Trigger servo to release the ball
            ball_servo.angle = 0  # Open position
            time.sleep(1)

            # Stop motors and reset servo
            stop_motors()
            ball_servo.angle = 90  # Closed position
            time.sleep(1)

except Exception as e:
    stop_motors()