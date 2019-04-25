import RPi.GPIO as gpio

# initializes and returns the servo
def initServo():
	channel = 12
	gpio.setmode(gpio.BOARD)
	gpio.setup(channel, gpio.OUT)
	servo = gpio.PWM(channel, 50)
	servo.start(7)
	return servo

# sets the speed of the servo with a value between -1 and 1
# -1 is full-speed counter-clockwise
# 0 is stopped
# 1 is full-speed clockwise
def setSpeed(servo, speed):
	if speed < -1 or speed > 1:
		raise ValueError('Expected a value for `speed` between -1 and 1')
	servo.ChangeDutyCycle(7 + 2 * speed)

# disposes of resources used by the servo
def disposeServo(servo):
	servo.stop()
	gpio.cleanup()
