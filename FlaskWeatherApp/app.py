import logging
from os import system
import requests
import paho.mqtt.client as paho
import threading
import json
import pandas as pd
import plotly
import plotly.express as px
import ssl
from time import sleep
from flask import Flask, render_template, request
import boto3 as AWS
from boto3.dynamodb.types import TypeDeserializer
import dynamo_json
from datetime import datetime
DEVICE_CHAUXDEFONDS="eui-70b3d5499d68c884"
DEVICE_RENENS="CapteurRenens"
app = Flask(__name__, static_url_path='',
			static_folder='static',
			template_folder='template')
app.config['DEBUG'] = True


class City:
    def __init__(self, name,weather,temperatureGraph ):
        self.name =name
        self.weather = weather
        self.temperatureGraph = temperatureGraph

@app.route('/', methods=['GET', 'POST'])
def index():
   # Get aws data

   # Get all different cities from json
    
    citiesNames= ["Renens", "La Chaux-de-Fonds"]

    url = 'http://api.openweathermap.org/data/2.5/weather?q={}&units=imperial&appid=271d1234d3f497eed5b1d80a07b3fcd1'
    urldynamodb = "https://108mjp0yek.execute-api.eu-west-1.amazonaws.com/default/GetWeatherTable?TableName=weather_app"
    dynamodb = requests.get(urldynamodb)
    dynamodbJson=dynamodb.json()
    items= dynamodbJson["Items"]


    database_unmarshalled_json='['
    for item in items:
        timestamp=int(float(item["sample_time"]["N"])/1000)
        sample_time=datetime.fromtimestamp(timestamp).strftime("%Y-%m-%dT%H:%M:%S.%f") 
        device_id=item["device_data"]["M"]["device_id"]["S"]
        temperature_1=item["device_data"]["M"]["decoded_payload"]["M"]["temperature_1"]["N"]
        relative_humidity_1=item["device_data"]["M"]["decoded_payload"]["M"]["relative_humidity_1"]["N"]
        luminosity_2=item["device_data"]["M"]["decoded_payload"]["M"]["luminosity_2"]["N"]
        altitude=item["device_data"]["M"]["decoded_payload"]["M"]["gps_1"]["M"]["altitude"]["N"]
        latitude=item["device_data"]["M"]["decoded_payload"]["M"]["gps_1"]["M"]["latitude"]["N"]
        longitude=item["device_data"]["M"]["decoded_payload"]["M"]["gps_1"]["M"]["longitude"]["N"]
        barometric_pressure_1=item["device_data"]["M"]["decoded_payload"]["M"]["barometric_pressure_1"]["N"]
        temperature_2=item["device_data"]["M"]["decoded_payload"]["M"]["temperature_2"]["N"]
        relative_humidity_2=item["device_data"]["M"]["decoded_payload"]["M"]["relative_humidity_2"]["N"]
        luminosity_1=item["device_data"]["M"]["decoded_payload"]["M"]["luminosity_1"]["N"]
        luminosity_2=item["device_data"]["M"]["decoded_payload"]["M"]["luminosity_2"]["N"]
        json_unmarshalled= {"sample_time": sample_time,"device_data":{"device_id" : device_id,"decoded_payload": {"temperature_1": temperature_1,"relative_humidity_1": relative_humidity_1,"gps_1": {"altitude": altitude,"latitude":latitude,"longitude":longitude},"barometric_pressure_1":barometric_pressure_1,"temperature_2": temperature_2,"relative_humidity_2": relative_humidity_2,"luminosity_1":luminosity_1,"luminosity_2": luminosity_2}}}
        unmarshalled=json.dumps(json_unmarshalled)
        database_unmarshalled_json+=unmarshalled+','
    database_unmarshalled_json=database_unmarshalled_json[:-1]
    database_unmarshalled_json+=']'
    df = pd.json_normalize(json.loads(database_unmarshalled_json))
    capteurRenens=df[df['device_data.device_id'].str.contains("CapteurRenens")]
    capteurCDF=df[df['device_data.device_id'].str.contains("eui-70b3d5499d68c884")]
    df_renens= capteurRenens.drop('device_data.device_id',1).sort_values(by=['sample_time'])
    df_CDF= capteurCDF.drop('device_data.device_id',1).sort_values(by=['sample_time'])
    cities =[]
    for cityName in citiesNames:
        #Evolution temperature
        
    #     dftest = pd.DataFrame({
	#   'Fruit': ['Apples', 'Oranges', 'Bananas', 'Apples', 'Oranges', 
	#   'Bananas'],
	#   'Amount': [4, 1, 2, 2, 4, 5],
	#   'City': ['SF', 'SF', 'SF', 'Montreal', 'Montreal', 'Montreal']
	# })
    #     fig2 = px.bar(dftest, x='Fruit', y='Amount', color='City', 
	#   barmode='group')

        # figTemp = px.line(df, x=df.index, y=df.columns,title='Temperature over time')
        # temperatureGraphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
        #figs.append(matchGraphJSONTemp)
        #Evolution pression
        #figTemp = px.line(df, x=df.index, y=df.columns,title='Données du match')
        #matchGraphJSONTemp = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
        #figs.append(matchGraphJSONTemp)
        #....
       
        if(cityName=="Renens"):
         fig = px.line(df_renens, x=df_renens['sample_time'], y=df_renens.columns,title='Station data') #,hover_data={"date": "|%B %d, %Y"},
        else:
         fig = px.line(df_CDF, x=df_CDF['sample_time'], y=df_CDF.columns,title='Station data') #,hover_data={"date": "|%B %d, %Y"},

         #fig.update_xaxes( dtick="M1",tickformat="%b\n%Y")
        GraphJSON =json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

        r = requests.get(url.format(cityName)).json()
        weather = {
            'city' : cityName,
            'temperature' : r['main']['temp'],
            'description' : r['weather'][0]['description'],
            'icon' : r['weather'][0]['icon'],
        }
        city = City(cityName,weather,GraphJSON) 
        cities.append(city)
   

       
    #df = pd.read_json('data.json')
	#df = read_data_csv("../../data/Passe_avant.csv")

    #fig.update_xaxes( dtick="M1",tickformat="%b\n%Y")
    return render_template('weather.html', cities=cities,)





####AWS 
   
connflag = False

def on_connect_sub(client, userdata, flags, rc):                # func for making connection
   print("Connection returned result: " + str(rc) )
   client.subscribe("/alarm", 1)
   client.subscribe("alarm", 1)

 
def on_message_sub(client, userdata, msg):                      # Func for Sending msg
   print(msg.topic+" "+str(msg.payload))
   
   global ack_response
   if("ACK" in str(msg.payload)): #text a modifier en fonction de la réponse reçu dans msg.payload
      ack_response = True
      print("ACK : " + str(ack_response))

def has_live_threads(threads):
    return True in [t.is_alive() for t in threads]

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

threads = []
  
# Create two threads as follows
logging.info("Main    : before creating thread")

x = threading.Thread(target=flaskRun)
x.start()
threads.append(x)
print("threads 1 started")

logging.info("Main    : before creating thread")
# y = threading.Thread(target=clientThreadSubscribe)
# y.start()
#threads.append(y)

print("threads 2 started")



while has_live_threads(threads):
        try:
            # synchronization timeout of threads kill
            [t.join(1) for t in threads
             if t is not None and t.is_alive()]
        except KeyboardInterrupt:
            # Ctrl-C handling and send kill to threads
            print("Sending kill to threads...")
            for t in threads:
                t.kill_received = True

print("Exited")
