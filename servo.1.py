import RPi.GPIO as gpio
import time

try:

	# initializes and returns the servo
	def initServo():
		channel = 12
		gpio.setmode(gpio.BOARD)
		gpio.setup(channel, gpio.OUT)
		servo = gpio.PWM(channel, 435)
		servo.start(65)
		return servo

	servo = initServo()

	#servo.ChangeDutyCycle(dc)

	for dc in range(30,100,5):
		servo.ChangeDutyCycle(dc)
		time.sleep(1)
		
	for dc in range(100,30,-5):
		servo.ChangeDutyCycle(dc)
		time.sleep(1)

# disposes of resources used by the servo
except KeyboardInterrupt:
	print('yeet')
	servo.stop()
	gpio.cleanup()
