from flask import Flask, request, render_template
import time
import datetime
import arrow

app = Flask(__name__)
app.debug = True # Make this False if you are no longer debugging


def validateDate(d):
    try:
        datetime.datetime.strptime(d, '%Y-%m-%d %H:%M')
        return True
    except ValueError:
	print "Error validating date"
        return False

@app.route("/")
def hello():
    return "Hello World!"

@app.route("/tempr")
def lab_temp():
        import sys
        import Adafruit_DHT
        humidity, temperature = Adafruit_DHT.read_retry(Adafruit_DHT.AM2302, 17)
        if humidity is not None and temperature is not None:
                return render_template("tempr.html",temp=temperature,hum=humidity)
        else:
                return render_template("no_sensor.html")

@app.route("/data")
def read_data():

        import sqlite3
        conn=sqlite3.connect('/home/pi/kedar/rpi3b/labs/dht.db')
        curs=conn.cursor()
        
	curs.execute("SELECT * FROM temperatures")
        temperatures = curs.fetchall()
        curs.execute("SELECT * FROM humidities")
	humidities = curs.fetchall()
        conn.close()
	
        return render_template("sdata.html",temp=temperatures,hum=humidities)


@app.route("/databydates", methods=['GET'])
def read_data_by_dates():

	fromDateStr = request.args.get('f',time.strftime("%Y-%m-%d %H:%M")) #Get the from date value from the URL
	toDateStr = request.args.get('t',time.strftime("%Y-%m-%d %H:%M"))   #Get the to date value from the URL


	if not validateDate(fromDateStr):    # Validate date before sending it to the DB
                fromDateStr = time.strftime("%Y-%m-%d 00:00")
        if not validateDate(toDateStr):
                toDateStr = time.strftime("%Y-%m-%d %H:%M")               


        import sqlite3
        conn=sqlite3.connect('/home/pi/kedar/rpi3b/labs/dht.db')
        curs=conn.cursor()
        
	curs.execute("SELECT * FROM temperatures WHERE read_datetime BETWEEN ? AND ?", (fromDateStr, toDateStr))
        temperatures = curs.fetchall()
	curs.execute("SELECT * FROM humidities WHERE read_datetime BETWEEN ? AND ?", (fromDateStr, toDateStr))
	humidities = curs.fetchall()
        conn.close()
	
        return render_template("sdata.html",temp=temperatures,hum=humidities)

@app.route("/data1", methods=['GET'])
def showData():
        temperatures, humidities, fromDateStr, toDateStr = indicatorData()
        return render_template( "data.html", temp                    = temperatures,
                                             hum                     = humidities,
                                             from_date               = fromDateStr,
                                             to_date                 = toDateStr,
                                             temp_items              = len(temperatures),
                                             hum_items               = len(humidities))

def indicatorData():

	fromDateStr = request.args.get('f',time.strftime("%Y-%m-%d %H:%M")) #Get the from date value from the URL
	toDateStr = request.args.get('t',time.strftime("%Y-%m-%d %H:%M"))   #Get the to date value from the URL
	fromRange = request.args.get('range_h','')  #returns a string, and emptry if no value 

	iRange = "nan"

	try:
		iRange = int(fromRange)
	except:
		print "range not a number"


	if not validateDate(fromDateStr):    # Validate date before sending it to the DB
                fromDateStr = time.strftime("%Y-%m-%d 00:00")
        if not validateDate(toDateStr):
                toDateStr = time.strftime("%Y-%m-%d %H:%M")               

        # If range_h is defined, we don't need the from and to times
        if isinstance(iRange,int):
        	timeNOW = datetime.datetime.now()
                timeFrom = timeNOW - datetime.timedelta(hours = iRange)
                timeTo = timeNOW
		fromDateStr = timeNOW.strftime("%Y-%m-%d 00:00")
                toDateStr = timeTo.strftime("%Y-%m-%d %H:%M")               
                

        import sqlite3
        conn=sqlite3.connect('/home/pi/kedar/rpi3b/labs/dht.db')
        curs=conn.cursor()

	print "from date: " + fromDateStr
	print "to date: " + toDateStr

	curs.execute("SELECT * FROM temperatures WHERE read_datetime BETWEEN ? AND ?", (fromDateStr, toDateStr))
        temperatures = curs.fetchall()
	curs.execute("SELECT * FROM humidities WHERE read_datetime BETWEEN ? AND ?", (fromDateStr, toDateStr))
	humidities = curs.fetchall()
        conn.close()
	
        return [temperatures,humidities,fromDateStr,toDateStr]


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8282)

