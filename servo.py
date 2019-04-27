import RPi.GPIO as gpio
import time

_median = 6.86
_started = False

# initializes and returns the servo
def initServo():
	channel = 12
	gpio.setmode(gpio.BOARD)
	gpio.setup(channel, gpio.OUT)
	servo = gpio.PWM(channel, 50)
	_started = False
	return servo

# sets the speed of the servo with a value between -1 and 1
# -1 is full-speed counter-clockwise
# 0 is stopped
# 1 is full-speed clockwise
def setSpeed(servo, speed):
	if speed == 0:
		stopServo(servo)
	elif speed < -1 or speed > 1:
		raise ValueError('Expected a value for `speed` between -1 and 1')
	else:
		startServo(servo)
	servo.ChangeDutyCycle(_median + 2 * speed)

# disposes of resources used by the servo
def disposeServo(servo):
	stopServo(servo)
	gpio.cleanup()

#starts the servo
def startServo(servo):
	if not _started:
		servo.start(_median)

#stops the servo
def stopServo(servo):
	if _started:
		servo.ChangeDutyCylce(0)
		servo.stop()

# rotates the servo 90 degrees and returns to resting position
def rotate90(servo, direction):
	setSpeed(servo, direction)
	time.sleep(0.20)
	setSpeed(servo, -direction)
	time.sleep(0.13)
	setSpeed(servo, 0)
	


