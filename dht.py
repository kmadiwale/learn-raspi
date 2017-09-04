from flask import Flask, request, render_template
app = Flask(__name__)
app.debug = True # Make this False if you are no longer debugging

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


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8282)

