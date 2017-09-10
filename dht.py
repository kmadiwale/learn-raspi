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
        temperatures, humidities, timezone, fromDateStr, toDateStr = indicatorData()

	#adding timezone support
	tz_tempr = []
	tz_humd = []

	for rec in temperatures:
		print rec
		local_timedate = arrow.get(rec[0], "YYYY-MM-DD HH:mm").to(timezone)
		tz_tempr.append([local_timedate.format('YYYY-MM-DD HH:mm'), round(rec[2],2)])

	for rec in humidities:
		local_timedate = arrow.get(rec[0], "YYYY-MM-DD HH:mm").to(timezone)
		tz_humd.append([local_timedate.format('YYYY-MM-DD HH:mm'), round(rec[2],2)])

	print "rendering template with: %s, %s, %s" % (timezone, fromDateStr, toDateStr)

        return render_template( "data.html", timezone 		     = timezone,
					     temp                    = tz_tempr,
                                             hum                     = tz_humd,
                                             from_date               = fromDateStr,
                                             to_date                 = toDateStr,
                                             temp_items              = len(temperatures),
                                             hum_items               = len(humidities),
					     query_String	     = request.query_string)

def indicatorData():

	fromDateStr = request.args.get('f',time.strftime("%Y-%m-%d %H:%M")) #Get the from date value from the URL
	toDateStr = request.args.get('t',time.strftime("%Y-%m-%d %H:%M"))   #Get the to date value from the URL
	timezone = request.args.get('timezone','Etc/UTC')
	fromRange = request.args.get('range_h','')  #returns a string, and emptry if no value 

	iRange = "nan"

	try:
		iRange = int(fromRange)
	except:
		print "range not a number"

	print "1. received from browser: %s, %s, %s, %s" % (fromDateStr, toDateStr, timezone, iRange)
	
	if not validateDate(fromDateStr):    # Validate date before sending it to the DB
                fromDateStr = time.strftime("%Y-%m-%d 00:00")
        if not validateDate(toDateStr):
                toDateStr = time.strftime("%Y-%m-%d %H:%M")               

	print '2. from: %s, to: %s, timezone: %s' % (fromDateStr,toDateStr,timezone)

        # Create datetime object so that we can convert to UTC from the browser's local time
        fromDate = datetime.datetime.strptime(fromDateStr,'%Y-%m-%d %H:%M')
        toDate = datetime.datetime.strptime(toDateStr,'%Y-%m-%d %H:%M')

        # If range_h is defined, we don't need the from and to times
        if isinstance(iRange,int):
        	#timeNOW = datetime.datetime.now()
                #timeFrom = timeNOW - datetime.timedelta(hours = iRange)
                #timeTo = timeNOW
		#fromDateStr = timeNOW.strftime("%Y-%m-%d 00:00")
                #toDateStr = timeTo.strftime("%Y-%m-%d %H:%M")               

		arrowTimeFrom = arrow.utcnow().replace(hours=-iRange)
                arrowTimeTo   = arrow.utcnow()
                fromDateUtc   = arrowTimeFrom.strftime("%Y-%m-%d %H:%M")
                toDateUtc     = arrowTimeTo.strftime("%Y-%m-%d %H:%M")
                fromDateStr   = arrowTimeFrom.to(timezone).strftime("%Y-%m-%d %H:%M")
                toDateStr     = arrowTimeTo.to(timezone).strftime("%Y-%m-%d %H:%M")
        else:
		#Convert datetimes to UTC so we can retrieve the appropriate records from the database
                fromDateUtc   = arrow.get(fromDate, timezone).to('Etc/UTC').strftime("%Y-%m-%d %H:%M")
                toDateUtc     = arrow.get(toDate, timezone).to('Etc/UTC').strftime("%Y-%m-%d %H:%M") 

        import sqlite3
        conn=sqlite3.connect('/home/pi/kedar/rpi3b/labs/dht.db')
        curs=conn.cursor()

	print "from date: " + fromDateStr
	print "to date: " + toDateStr

	#curs.execute("SELECT * FROM temperatures WHERE read_datetime BETWEEN ? AND ?", (fromDateStr, toDateStr))
	curs.execute("SELECT * FROM temperatures WHERE read_datetime BETWEEN ? AND ?", (fromDateUtc.format('YYYY-MM-DD HH:mm'), toDateUtc.format('YYYY-MM-DD HH:mm')))
        temperatures = curs.fetchall()
	#curs.execute("SELECT * FROM humidities WHERE read_datetime BETWEEN ? AND ?", (fromDateStr, toDateStr))
	curs.execute("SELECT * FROM humidities WHERE read_datetime BETWEEN ? AND ?", (fromDateUtc.format('YYYY-MM-DD HH:mm'), toDateUtc.format('YYYY-MM-DD HH:mm')))
	humidities = curs.fetchall()
        conn.close()
	
        return [temperatures,humidities,timezone,fromDateStr,toDateStr]


@app.route("/to_plotly", methods=['GET'])  #This method will send the data to ploty.
def to_plotly():
        import plotly.plotly as py
        from plotly.graph_objs import *
	import json

	#important code to login into plotly -- starts	
	with open('/home/pi/.plotly/.credentials') as config_file:
		plotly_user_config = json.load(config_file)

	username = plotly_user_config['username']
	apiKey = plotly_user_config['api_key']

	py.sign_in(username, apiKey)
	#important code to login into plotly -- ends
	

        temperature, humidities, timezone, from_date_str, to_date_str = indicatorData()

        # Create new record tables so that datetimes are adjusted back to the user browser's time zone.
        time_series_adjusted_tempreratures  = []
        time_series_adjusted_humidities         = []
        time_series_temprerature_values         = []
        time_series_humidity_values             = []

        for record in temperatures:
                local_timedate = arrow.get(record[0], "YYYY-MM-DD HH:mm").to(timezone)
                time_series_adjusted_tempreratures.append(local_timedate.format('YYYY-MM-DD HH:mm'))
                time_series_temprerature_values.append(round(record[2],2))

        for record in humidities:
                local_timedate = arrow.get(record[0], "YYYY-MM-DD HH:mm").to(timezone)
                time_series_adjusted_humidities.append(local_timedate.format('YYYY-MM-DD HH:mm')) #Best to pass datetime in text

             #so that Plotly respects it
                time_series_humidity_values.append(round(record[2],2))

        temp = Scatter(
                        x=time_series_adjusted_tempreratures,
                        y=time_series_temprerature_values,
                        name='Temperature'
                                )
        hum = Scatter(
                        x=time_series_adjusted_humidities,
                        y=time_series_humidity_values,
                        name='Humidity',
                        yaxis='y2'
                                )

        data = Data([temp, hum])

        layout = Layout(
                                        title="Temperature and humidity in the lab",
                                    xaxis=XAxis(
                                        type='date',
                                        autorange=True
                                    ),
                                    yaxis=YAxis(
                                        title='Celcius',
                                        type='linear',
                                        autorange=True
                                    ),
                                    yaxis2=YAxis(
                                        title='Percent',
                                        type='linear',
                                        autorange=True,
                                        overlaying='y',
                                        side='right'
                                    )

                                        )
        fig = Figure(data=data, layout=layout)
        plot_url = py.plot(fig, filename='dht')
	print plot_url
        return plot_url


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8282)

