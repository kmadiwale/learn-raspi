#FILE NAME: blinky.py
#------------------------------------------------
#1. WHAT IT DOES: makes an LED blink 
#------------------------------------------------
#2. REQUIRES
#------------------------------------------------
# Raspberry Pi
# A 5mm LED
# A 1KOhm resistor
# Jumper wires
#------------------------------------------------

import RPi.GPIO as GPIO         ## Import GPIO Library
import time                     ## Import 'time' library (for 'sleep')
 
pin = 5                         ## We're working with assigned pin
GPIO.setmode(GPIO.BOARD)        ## Use BOARD pin numbering
GPIO.setup(pin, GPIO.OUT)       ## Setting assigned pin to OUTPUT

for i in range (0, 20):         ## Repeat 20 times
	GPIO.output(pin, GPIO.HIGH) ## Turn on GPIO pin (HIGH)
	time.sleep(1)               ## Wait 1 second
	GPIO.output(pin, GPIO.LOW)  ## Turn off GPIO pin (LOW)
	time.sleep(1)               ## Wait 1 second
 
GPIO.cleanup()
print "thank you for enlightening me!"
