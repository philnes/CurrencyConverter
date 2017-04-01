#!/usr/bin/env python
# Author: H.H.N.P.
# Use: python fhtw_rest_EZB.py

# ---------- imports ----------
from flask import Flask		# http://flask.pocoo.org/
from flask import jsonify
from flask import request
import urllib2
from xml.dom import minidom
import time
import threading
from flask import make_response
from flask.ext.httpauth import HTTPBasicAuth
import os.path
# ---------- end of imports ----------

app = Flask(__name__)
auth = HTTPBasicAuth()
exchanges = {}

banner = '\n'            
banner += '@@@@@@@@  @@@  @@@  @@@@@@@  @@@  @@@  @@@  \n'
banner += '@@@@@@@@  @@@  @@@  @@@@@@@  @@@  @@@  @@@  \n'
banner += '@@!       @@!  @@@    @@!    @@!  @@!  @@!  \n'
banner += '!@!       !@!  @!@    !@!    !@!  !@!  !@!  \n'
banner += '@!!!:!    @!@!@!@!    @!!    @!!  !!@  @!@  \n'
banner += '!!!!!:    !!!@!!!!    !!!    !@!  !!!  !@!  \n'
banner += '!!:       !!:  !!!    !!:    !!:  !!:  !!:  \n'
banner += ':!:       :!:  !:!    :!:    :!:  :!:  :!:  \n'
banner += ' ::       ::   :::     ::     :::: :: :::   \n'
banner += ' :         :   : :     :       :: :  : : \n'


# curl -u username:password -i http://localhost:5000/exchange/getAll
@auth.get_password
def get_password(username):
    if username == 'bill':
        return 'gates'
    return None


@auth.error_handler
def unauthorized():
    return make_response(jsonify({'error': 'Unauthorized access'}), 401)


# curl -i http://localhost:5000/exchange/getRate/USD
@app.route('/exchange/getRate/<currency>',methods=['GET'])
def getRateForCur(currency):
	return jsonify({currency:exchanges.get(currency)})


# curl -i http://localhost:5000/exchange/getAll
@app.route('/exchange/getAll',methods=['GET'])
@auth.login_required
def getAll():
	return jsonify({'EZB':exchanges})

@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


def getDataFromEZB():
	print '[*] gathering data ...'
	url_str = 'http://www.ecb.europa.eu/stats/eurofxref/eurofxref-daily.xml' # EZB XML-URL
	xml_str = urllib2.urlopen(url_str)

	# create exchange.xml or update existing one
	file = open('exchange.xml','w')
	for line in xml_str:
		file.write(line)
	file.close()
	print '[*] data gathered!'


def transformData():
	if(os.path.isfile('exchange.xml')):
		print '[*] transforming data ...'
		doc = minidom.parse("exchange.xml")
		tag = doc.getElementsByTagName("Cube")

		for i in tag:
			cur = i.getAttribute("currency")
			cur = cur.encode('ascii')	# otherwise the dictionary will be filled with binary values
			rate = i.getAttribute("rate")
			rate = rate.encode('ascii')
			if(len(cur)>=2):		
				exchanges[cur] = rate
		print '[*] data transformed!'
	else:
		print '[ ERROR ] No historical data found. Reconnect to the internet and restart the service!'


def doYourFuckingJob():
	try:
		getDataFromEZB()
		transformData()
		print '[!] data update finished %s' % time.ctime()
		#threading.Timer(86400,doYourFuckingJob).start() # update data information after 24 hours
		return 1
	except:
		print '[ ERROR ] Something went wrong! Check your internet connection!'
		print '[ ERROR ] Let\'s try to use some historical data...'
		try:
			transformData()
			return 1
		except:
			return 0


if __name__ == "__main__":
	print banner
	keep_processing = doYourFuckingJob()
	if(keep_processing == 1):
		app.run() #app.run(host='0.0.0.0', port=80)
