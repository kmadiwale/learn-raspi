from flask import Flask
from flask import render_template

app = Flask(__name__)
app.debug=True

@app.route("/")
def hello():
	#return "Hello World! using uWSGI"
	return render_template('hello.htl', message="Hello Kedar!")

if __name__ == "__main__":
	app.run(host='0.0.0.0', port=8282)

