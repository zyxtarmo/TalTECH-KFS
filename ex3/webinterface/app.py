# Store this code in 'app.py' file

from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
import paho.mqtt.client as paho
import MySQLdb.cursors
import re
import uuid
import logging

app = Flask(__name__)
# Configure logging settings
logging.basicConfig(level=logging.DEBUG)  # Set logging level to DEBUG

app.secret_key = 'your secret key'

app.config['MYSQL_HOST'] = '10.8.0.1'
app.config['MYSQL_USER'] = 'kala'
app.config['MYSQL_PASSWORD'] = 'ujubvees'
app.config['MYSQL_DB'] = 'akvaarium'

# broker
broker="10.8.0.1"
broker_pass = "parool"
broker_username = "iot_module"
client_id = str(uuid.uuid4().urn[9:])

mysql = MySQL(app)

# Define callback
def on_message(client, userdata, message):
    print("received message =", str(message.payload.decode("utf-8")))

# init mqtt
mqtt_client = paho.Client(paho.CallbackAPIVersion.VERSION1, "web-%s" % client_id)
# Bind function to callback
mqtt_client.on_message = on_message
# Set username and password
mqtt_client.username_pw_set(username = broker_username, password = broker_pass)
mqtt_client.connect(broker)   # connect
mqtt_client.loop_start()

@app.route('/')
def index():
	if session.get('loggedin'):		
		return render_template('index.html', uid = session['id'])
	else:
		return redirect(url_for('login'))

@app.route('/login', methods =['GET', 'POST'])
def login():
	msg = ''
	if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
		username = request.form['username']
		password = request.form['password']
		cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
		cursor.execute('SELECT * FROM accounts WHERE username = % s AND password = % s', (username, password, ))
		account = cursor.fetchone()
		if account:
			session['loggedin'] = True
			session['id'] = account['id']
			session['username'] = account['username']
			msg = 'Logged in successfully !'
			return render_template('index.html', msg = msg, uid=session['id'])
		else:
			msg = 'Incorrect username / password !'
	return render_template('login.html', msg = msg)

@app.route('/logout')
def logout():
	session.pop('loggedin', None)
	session.pop('id', None)
	session.pop('username', None)
	return redirect(url_for('login'))

@app.route('/device', methods =['GET', 'POST'])
def device():
	if session.get('loggedin'):
		userid = request.args.get('uid', default = 1, type = int)
		cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
		cursor.execute('SELECT * FROM devices WHERE userid = % s', (userid, ))
		devrow = cursor.fetchone()
		if devrow:
			return render_template('device.html', deviceid = devrow['uuid'], uid = userid)
		else:
			return render_template('device.html', deviceid = 'NA', uid = userid)

@app.route('/message', methods =['GET', 'POST'])
def message():
	if request.method == 'POST' and 'message' in request.form and 'deviceid' in request.form:
		message = request.form['message']
		client_id = request.form['deviceid']
		mqtt_client.publish("akvaarium/%s" % client_id, message)
		app.logger.info("Message to: akvaarium/%s" % client_id)
		return redirect(url_for('device'))

@app.route('/register', methods =['GET', 'POST'])
def register():
	msg = ''
	if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form :
		username = request.form['username']
		password = request.form['password']
		email = request.form['email']
		cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
		cursor.execute('SELECT * FROM accounts WHERE username = % s', (username, ))
		account = cursor.fetchone()
		if account:
			msg = 'Account already exists !'
		elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
			msg = 'Invalid email address !'
		elif not re.match(r'[A-Za-z0-9]+', username):
			msg = 'Username must contain only characters and numbers !'
		elif not username or not password or not email:
			msg = 'Please fill out the form !'
		else:
			cursor.execute('INSERT INTO accounts VALUES (NULL, % s, % s, % s)', (username, password, email, ))
			mysql.connection.commit()
			msg = 'You have successfully registered !'
	elif request.method == 'POST':
		msg = 'Please fill out the form !'
	return render_template('register.html', msg = msg)

if __name__ == '__main__':
    app.run(debug=True)