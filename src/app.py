from flask import Flask, render_template, request, make_response, jsonify, session, Markup
from flask_session import Session
import memcache
import os
import socket
from user import User
import redis
from correlation import Correlation
from frequency import Frequency

app = Flask(__name__)

SESSION_TYPE = 'filesystem'
app.config.from_object(__name__)
Session(app)

# Home page - Will display either login screen or dashboard
@app.route("/")
def displayHomepage():

	if not User.isLoggedIn():
		response = render_template('login.html')
	else:
		response = render_template('dashboard.html', firstName = User.getFirstName())

	return response

# Authentication page
@app.route("/login", methods=['POST'])
def checkCredentials():

	login = User()

	return login.checkCredentials(email = request.form['email'], password = request.form['password'])

# Authentication page
@app.route("/register", methods=['GET', 'POST'])
def renderRegisterPage():

	register = User()

	if request.method == "GET":
		return render_template('register.html')
	if request.method == "POST":
		userRegistration = register.registerUser(request.form['firstName'], request.form['lastName'], request.form['address'], request.form['city'], request.form['state'], request.form['zip'], request.form['email'], request.form['password'])
		return render_template('register.html', errorMessage = userRegistration)

# correlation page
@app.route("/correlation", methods=['GET', 'POST'])
def renderCorrelation():

	correlation = Correlation()

	if request.method == "GET":
		return render_template('associate.html')
	if request.method == "POST":
		correlationResults = correlation.correlateWines(request.form['wine_type'], 'quality', request.form['wine_characteristic'])
		characteristicValues = correlation.getCharacteristicValues(request.form['wine_type'])
		regressionLineValues = correlation.generateRegressionLine()
		return render_template('association-graph.html', results = Markup(correlationResults), qualityValues = characteristicValues['quality'], otherValues = characteristicValues[request.form['wine_characteristic']], yAxisTitle = request.form['wine_characteristic'].title(), regressionValues = regressionLineValues)

# correlation page
@app.route("/frequency", methods=['GET', 'POST'])
def renderFrequency():

	frequency = Frequency()

	if request.method == "GET":
		return render_template('frequency.html')
	if request.method == "POST":
		frequencyDist = frequency.getFrequency(request.form['wine_type'], request.form['wine_characteristic_value'], request.form['wine_characteristic'], 'quality')
		return render_template('frequency-graph.html', results = Markup(frequencyDist[0]), wineChars = frequencyDist[1], wineChar = frequencyDist[2].title())

@app.route("/logout")
def logoutUser():
	return User.logout()

# 404 - No page exists
@app.errorhandler(404)
def render(error):

	return "Oh no... I found nothing"

if __name__ == "__main__":
	# NOTE: debug mode necessary if you want to see live reloads
    #port = int(os.environ.get('PORT', 4000))
    #app.run(host='0.0.0.0', port=port)
    app.run(debug = True, host='0.0.0.0', port=80)
