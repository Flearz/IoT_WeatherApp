import socket
import time
import ubinascii
import pycom
from pycoproc_2 import Pycoproc
from network import WLAN
import machine
from  AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
import json

from LIS2HH12 import LIS2HH12
from SI7006A20 import SI7006A20
from LTR329ALS01 import LTR329ALS01
from MPL3115A2 import MPL3115A2,ALTITUDE,PRESSURE
#!/usr/bin/env python
#
# Copyright (c) 2020, Pycom Limited.
#
# This software is licensed under the GNU GPL version 3 or any
# later version, with permitted additional terms. For more information
# see the Pycom Licence v1.0 document supplied with this file, or
# available at https://www.pycom.io/opensource/licensing
#

# See https://docs.pycom.io for more information regarding library specifics


########## GET PYSENSE DATA
#pycom.heartbeat(True)
# pycom.rgbled(0x0A0A08) # white

# pycom.heartbeat(False)
# pycom.rgbled(0x0A0A08) # white


def printValues():
    mp = MPL3115A2(mode=ALTITUDE) # Returns height in meters. Mode may also be set to PRESSURE, returning a value in Pascals
    print("MPL3115A2")
    print("Temperature: " + str(mp.temperature()))
    print("Altitude: " + str(mp.altitude()))
    mpp = MPL3115A2(mode=PRESSURE) # Returns pressure in Pa. Mode may also be set to ALTITUDE, returning a value in meters
    print("Pressure: " + str(mpp.pressure()))


    si = SI7006A20()
    print("SI7006A20")
    print("Temperature: " + str(si.temperature())+ " deg C and Relative Humidity: " + str(si.humidity()) + " %RH")
    print("Dew point: "+ str(si.dew_point()) + " deg C")
    t_ambient = 24.4
    temperatureMean = (mp.temperature() + si.temperature())/2

    print("Humidity Ambient for " + str(t_ambient) + " deg C is " + str(si.humid_ambient(t_ambient)) + "%RH")
    print("Humidity Ambient for " + str(temperatureMean) + " deg C is " + str(si.humid_ambient(temperatureMean)) + "%RH")

    print("Temperature mean:{temperatureMean}".format(temperatureMean=temperatureMean))
    lt = LTR329ALS01()
    print("Light (channel Blue lux, channel Red lux): " + str(lt.light()))

# printValues()



DEVICENAME="CapteurRenens"




###########################
###########################


# Initialise Wifi connection to the router
# https://docs.pycom.io/tutorials/networks/wlan/


wlan = WLAN(mode=WLAN.STA)

# connection to wlan
nets = wlan.scan()
print(nets)
for net in nets:
    # if net.ssid == 'CollocHT':
    #     print('Network found!')
    #     wlan.connect(net.ssid, auth=(net.sec, 'henrithibaud'), timeout=5000)
    #     print("connecting",end='')
    #     while not wlan.isconnected():
    #         time.sleep(1)
    #         print(".",end='')
    #     print('WLAN connection succeeded!')
    #     break
    if net.ssid == 'P50HENRI':
        print('Network found!')
        wlan.connect(net.ssid, auth=(net.sec, 'jatonlmchm'), timeout=10000)
        print("connecting",end='')
        while not wlan.isconnected():
            time.sleep(1)
            print(".",end='')
        print('WLAN connection succeeded!')
    # if net.ssid == 'FRANTZENT':
    #     print('Network found!')
    #     wlan.connect(net.ssid, auth=(net.sec, '-06F43y3'), timeout=10000)
    #     print("connecting",end='')
    #     while not wlan.isconnected():
    #         time.sleep(1)
    #         print(".",end='')
    #     print('WLAN connection succeeded!')
    # break
#connected

####AWS 
# user specified callback function
def customCallback(client, userdata, message):
	print("Received a new message: ")
	print(message.payload)
	print("from topic: ")
	print(message.topic)
	print("--------------\n\n")


TOPIC= "capteurwifi"
HOST="a2jrpgf4bh14vn-ats.iot.eu-west-1.amazonaws.com"
PORT = 8883                                              # Port no.   
clientId = "capteur_client"                                     # Thing_Name
thingName = "capteur_thing"                                    # Thing_Name
caPath = "/flash/cert/AmazonRootCA1.pem"                                      # Root_CA_Certificate_Name
certPath = "/flash/cert/c2f2ce2a1866e4b7aaa89cf1769d61a0f6b6e8c07320e00734aa566520513447-certificate.pem.crt"                            # <Thing_Name>.cert.pem
keyPath = "/flash/cert/c2f2ce2a1866e4b7aaa89cf1769d61a0f6b6e8c07320e00734aa566520513447-private.pem.key"                          # <Thing_Name>.private.key
# configure the MQTT client
pycomAwsMQTTClient = AWSIoTMQTTClient(clientId)
pycomAwsMQTTClient.configureEndpoint(HOST, PORT)
pycomAwsMQTTClient.configureCredentials(caPath, keyPath, certPath)

# pycomAwsMQTTClient.configureOfflinePublishQueueing(config.OFFLINE_QUEUE_SIZE)
# pycomAwsMQTTClient.configureDrainingFrequency(config.DRAINING_FREQ)
# pycomAwsMQTTClient.configureConnectDisconnectTimeout(config.CONN_DISCONN_TIMEOUT)
# pycomAwsMQTTClient.configureMQTTOperationTimeout(config.MQTT_OPER_TIMEOUT)
# pycomAwsMQTTClient.configureLastWill(config.LAST_WILL_TOPIC, config.LAST_WILL_MSG, 1)

#Connect to MQTT Host
if pycomAwsMQTTClient.connect():
    print('AWS connection succeeded')

# # Subscribe to topic
# pycomAwsMQTTClient.subscribe(TOPIC, 1, customCallback)
# time.sleep(2)

# Send message to host
while True:
    mp = MPL3115A2(mode=ALTITUDE) # Returns height in meters. Mode may also be set to PRESSURE, returning a value in Pascals

    mpTemperature=mp.temperature()
    mpAltitude=mp.altitude()

    mpp = MPL3115A2(mode=PRESSURE) # Returns pressure in Pa. Mode may also be set to ALTITUDE, returning a value in meters
    mppPressure=mpp.pressure()

    si = SI7006A20()
    siTemperature=si.temperature()
    siRelativeHumidity=si.humidity()
    siDewPoint=si.dew_point()
    temperatureMean = (mpTemperature+ siTemperature)/2
    siAmbientHumidity=si.humid_ambient(temperatureMean)
    lt = LTR329ALS01()
    lighttuple=lt.light()
    blue=lighttuple[0]
    red=lighttuple[1]
    #paylodmsg= '{"data": {"device name" : "{devicename}","temperature": "{temperature}","altitude": "{altitude}","pressure": "{pressure}","dew point": "{dew}","humidity": "{humidity}","light": {"red": "{red}","blue": "{blue}"/}/}/}'
    paylodmsg= {"device_id" : DEVICENAME,"decoded_payload": {"temperature_1": temperatureMean,"relative_humidity_1": siRelativeHumidity,"gps_1": {"altitude": mpAltitude,"latitude":46,"longitude":6},"barometric_pressure_1": mppPressure/100,"temperature_2": siDewPoint,"relative_humidity_2": siAmbientHumidity,"luminosity_1":blue,"luminosity_2": red}}
    #paylodmsg.format(devicename = DEVICENAME, temperature= str(temperatureMean),altitude=str(mp.altitude()),pressure=str(mpp.pressure()), dew=str(si.dew_point()),humidity=str(si.humid_ambient(temperatureMean)),red=str(red),blue=str(blue))
    paylodmsg = json.dumps(paylodmsg) 
    # payload={"payload":paylodmsg}
    # paylodmsg = json.dumps(payload) 
    print(paylodmsg)
    #paylodmsg_json = json.loads(paylodmsg)       
    pycomAwsMQTTClient.publish(TOPIC, paylodmsg, 1)
    time.sleep(10)