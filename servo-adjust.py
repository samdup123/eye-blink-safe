from servo import *

# rotates the servo 90 degrees and returns to resting position
def adjust(servo, direction):
	setSpeed(servo, direction)
	time.sleep(0.01)
	setSpeed(servo, 0)
	
servo = initServo()
adjust(servo, -1)
