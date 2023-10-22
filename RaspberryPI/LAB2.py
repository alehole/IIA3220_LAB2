from gpiozero import MCP3002
import RPi.GPIO as GPIO
import thingspeak
import time
import re
from datetime import datetime
from PID import *
from Tmr import *
import pymongo



# Read MCP3002 ADC channel
adc = MCP3002(channel=1, differential=False)
def TMP36_C(channel, offset):
	adcdata = adc.value; 		# Value between 0 and 1
	voltvalue = adcdata * 5;	# Convert to volt
	return 100*voltvalue-50 + offset	# Temp in celsius

# Write to thingspeak channel
def write_ts_ch(field, value):
	channel_id = 2249580
	write_key = "3NOE8V32EDL4MQMU"
	channel = thingspeak.Channel(id = channel_id, api_key = write_key)
	response = channel.update({field: value})
		
# Read thingspeak channel
def read_ts_ch():
	channel_id = 2249580
	read_key = "2B6PR61ZTQWTDSVU"
	channel = thingspeak.Channel(id=channel_id, api_key=read_key)
	value = channel.get_field_last(field="field1")
	#print(value)
	numbers = re.findall(r'\d+', value)
	result = list(map(int, numbers))
	temperature = float( str(result[8]) + str(result[9]))/100
	print("Temperature is " + str( temperature) + " celsius")

def Updt_MongoDB_Srv(Value, client, database, collection):
	now = datetime.now()
	datetimeformat = "%Y --%m --%d %H:%M:%S"
	MeasurementDateTime = now.strftime(datetimeformat)
	document = { "MeasurementValue": Value , "MeasurementDateTime":MeasurementDateTime} # Insert Data into Database
	x = collection.insert_one (document)
	
def printDb(collection):
	for x in collection.find():
		print(x)
		
		
# HiveMQTT Stuff
# setting callbacks for different events to see if it works, print the message etc.
def on_connect(client, userdata, flags, rc, properties=None):
	print("CONNACK received with code %s." % rc)

# with this callback you can see if your publish was successful
def on_publish(client, userdata, mid, properties=None):
	print("mid: " + str(mid))

# print which topic was subscribed to
def on_subscribe(client, userdata, mid, granted_qos, properties=None):
	print("Subscribed: " + str(mid) + " " + str(granted_qos))
