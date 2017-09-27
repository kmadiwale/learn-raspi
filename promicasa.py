#------------------------------------
# Home security system. 092517
#-----------------------------------

import RPi.GPIO as GPIO
import time, datetime
import os, sys

sys.path.insert(0, "/usr/bin/raspistill")

def click(f):
	print("Intrusion detected by pir1, capturing image: " + f)
	os.system('raspistill -o ' + f + ' --nopreview --exposure sports --timeout 1')
	
GPIO.setmode(GPIO.BCM)

imgPath = '/home/pi/kedar/rpi3b/images/'
pir=14
buzz=15
dts='%Y-%m-%d.%H-%M-%S'

GPIO.setup(pir, GPIO.IN)
GPIO.setup(buzz, GPIO.OUT)
GPIO.output(buzz, GPIO.LOW)

time.sleep(5) #setting up the sensor
print ("sensor is ready!")

x=GPIO.input(pir)
if x==1:
	GPIO.output(buzz, GPIO.HIGH)
	fname = 'IMG_intrusion_' + datetime.datetime.now().strftime(dts) + '.jpg'
	click(imgPath + fname)
	GPIO.output(buzz, GPIO.LOW)

GPIO.cleanup()
print("resources cleaned up")

