# FILE NAME: button.py
#------------------------------------------------
# WHAT IT DOES
# Reads the status of a button using a Raspberry Pi.
#------------------------------------------------
# Any Raspberry Pi
# A pushbutton
# A 10kOhm resistor
# Jumper wires
# A breadboard
#------------------------------------------------

import RPi.GPIO as GPIO   ## Import GPIO Library
 
inPin = 5                 ## Switch connected to pin 8
GPIO.setmode(GPIO.BOARD)    ## Use BOARD pin numbering
GPIO.setup(inPin, GPIO.IN)  ## Set pin 5 to INPUT
 
while True:                 ## Do this forever
    value = GPIO.input(inPin) ## Read input from switch
    if value:                 ## If switch is released
        print "Not Pressed"
    else:                     ## Else switch is pressed
        print "Pressed"
 
GPIO.cleanup() 
