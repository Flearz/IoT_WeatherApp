import logging
from os import system
import requests
import paho.mqtt.client as paho
import threading
import json
import ssl
from time import sleep
from flask import Flask, render_template, request

app = Flask(__name__, static_url_path='',
			static_folder='static',
			template_folder='template')
app.config['DEBUG'] = True


class City():
    name =""

@app.route('/', methods=['GET', 'POST'])
def index():
   # Get aws data

   # Get all different cities from json
    
    cities= ["Renens", "La Chaux-de-Fonds"]

    url = 'http://api.openweathermap.org/data/2.5/weather?q={}&units=imperial&appid=271d1234d3f497eed5b1d80a07b3fcd1'

    weather_data = []

    for city in cities:

        r = requests.get(url.format(city)).json()

        weather = {
            'city' : city,
            'temperature' : r['main']['temp'],
            'description' : r['weather'][0]['description'],
            'icon' : r['weather'][0]['icon'],
        }

        weather_data.append(weather)


    return render_template('weather.html', weather_data=weather_data)


####AWS 
   
connflag = False

def on_connect_sub(client, userdata, flags, rc):                # func for making connection
   print("Connection returned result: " + str(rc) )
   client.subscribe("/appmobile", 1)
   client.subscribe("appmobile", 1)

 
def on_message_sub(client, userdata, msg):                      # Func for Sending msg
   print(msg.topic+" "+str(msg.payload))
   
   global ack_response
   if("ACK" in str(msg.payload)): #text a modifier en fonction de la réponse reçu dans msg.payload
      ack_response = True
      print("ACK : " + str(ack_response))



def clientThreadSubscribe():
	mqttc2 = paho.Client()                                       # mqttc object
	mqttc2.on_connect = on_connect_sub                               # assign on_connect func
	mqttc2.on_message = on_message_sub                               # assign on_message func
	#mqttc.on_log = on_log
	#### Change following parameters #### 
	awshost = "a2c3m8slscjp9m-ats.iot.us-east-2.amazonaws.com"      # Endpoint	
	awsport = 8883                                              # Port no.   
	clientId = "Flask"                                     # Thing_Name
	thingName = "Flask"                                    # Thing_Name
	caPath = "./AmazonRootCA1.pem"                                      # Root_CA_Certificate_Name
	certPath = "./c0edf1ae0656ddb0cdd9d3b41fcf7abbaaecc4a327007223fe8ee287bddc7497-certificate.pem.crt"                            # <Thing_Name>.cert.pem
	keyPath = "./c0edf1ae0656ddb0cdd9d3b41fcf7abbaaecc4a327007223fe8ee287bddc7497-private.pem.key"                          # <Thing_Name>.private.key
	 
	mqttc2.tls_set(caPath, certfile=certPath, keyfile=keyPath, cert_reqs=ssl.CERT_REQUIRED, tls_version=ssl.PROTOCOL_TLSv1_2, ciphers=None)      
	 
	mqttc2.connect(awshost, awsport, keepalive=60)               # connect to aws server
	 
	mqttc2.loop_forever()

def flaskRun():
	app.run(host='0.0.0.0',port='80',debug=False)

  
# Create two threads as follows
logging.info("Main    : before creating thread")

x = threading.Thread(target=flaskRun)
x.start()
print("threads 1 started")

logging.info("Main    : before creating thread")
# y = threading.Thread(target=clientThreadSubscribe)
# y.start()

print("threads 2 started")
try:
	while True:
	   sleep(2)
except KeyboardInterrupt:
	system.exit(0)
