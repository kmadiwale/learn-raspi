#------------------------------------
# Home security system. 092817
#-----------------------------------
import RPi.GPIO as GPIO
import time, datetime
import os, sys
import sqlite3
import smtplib
import configparser
import logging

from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
from email.MIMEBase import MIMEBase
from email import encoders

sys.path.insert(0, "/usr/bin/raspistill")

logger = logging.getLogger('casa')
lhdlr = logging.FileHandler('/home/pi/rpi3b/hs7/casa.log')
frmtr = logging.Formatter('%(asctime)s %(levelname)s %(message)s')

lhdlr.setFormatter(frmtr)
logger.addHandler(lhdlr)
logger.setLevel(logging.WARNING)

def save(pir_id, img2Save):
	logger.info("saving data, please wait...")
	conn=sqlite3.connect('/home/pi/rpi3b/hs7/intruder.db')  
        curs=conn.cursor()
        curs.execute("""INSERT INTO intruder values(datetime(CURRENT_TIMESTAMP, 'localtime'),(?), (?))""", (pir_id, img2Save))
        conn.commit()
        conn.close()
	logger.info("movement logged")


def click(f, pir_id):
	logger.info("movement detected by " + pir_id + ", capturing image, hope you smiled: " + f)
	os.system('raspistill -o ' + f + ' --nopreview --exposure sports --timeout 1')


def notify(from_id, email_id, subject, smtp, port, phrase, pir_id, img, capTime):
	logger.info("notifying...")
	message = MIMEMultipart()
	#build message
	message['From'] = from_id
	message['To'] = email_id
	message['Subject'] = subject
	#build message body and attachment
	msgBody = "PFA Intruder image from " + pir_id + " @ " + str(capTime)
	message.attach(MIMEText(msgBody, 'html'))
	iAttach = open(img, "rb")
	part = MIMEBase('application','octet-stream')
	part.set_payload((iAttach).read())
	encoders.encode_base64(part)
	part.add_header('Content-Disposition', "attachment;filename=%s"%img[len(imgPath):])
	message.attach(part)
	#prepare to send email
	server=smtplib.SMTP(str(smtp), int(port))
	server.starttls()
	server.login(from_id, phrase)
	text=message.as_string()
	server.sendmail(from_id, email_id, text)
	server.quit()
	logger.info("Please check your email for intruder attachment")

#program begin
if (len(sys.argv) > 1):
	away = isinstance(sys.argv[1], bool)
	logger.info("away, notification:true")
else:
	away = False
	logger.error("not away, notification:false")

imgPath = '/home/pi/rpi3b/hs7/images/'
dts='%Y-%m-%d.%H-%M-%S'

config = configparser.ConfigParser()
config.read('/home/pi/rpi3b/hs7/casa.ini')

pir1=int(config.get('pi','pir1'))
buzz=int(config.get('pi','buzz'))

GPIO.setmode(GPIO.BCM)
GPIO.setup(pir1, GPIO.IN)
GPIO.setup(buzz, GPIO.OUT)
GPIO.output(buzz, GPIO.LOW)

time.sleep(60) #setting up the sensor
logger.info("sensor is ready!")

while True:
	x=GPIO.input(pir1)
	if x==1:
		GPIO.output(buzz, GPIO.HIGH)
		captureTime = datetime.datetime.now().strftime(dts)
		fname = 'IMG_intrusion_' + captureTime + '.jpg'
		click(imgPath + fname, "PIR1")
		GPIO.output(buzz, GPIO.LOW)
		save("PIR1", imgPath + fname)
		if (away):
			notify(config.get('mail','se_id'), config.get('mail','re_id'), config.get('mail', 'se_sub'), 
			config.get('mail', 'se_pro'),config.get('mail', 'se_pro_port'), config.get('mail', 'se_phrase'), 
			"PIR1", imgPath + fname, captureTime)
		time.sleep(1) #pause for 1 second(s) before proceeding


GPIO.cleanup()
logger.info("resources cleaned up")

