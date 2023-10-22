from LAB2 import *
import pymongo
import smbus
import paho.mqtt.client as paho
from paho import mqtt

# TC74 I2C setup
channel= 1
address = 0x4d
bus = smbus.SMBus(channel)

GPIO.setup(20, GPIO.IN) # Pushbutton for alarm ack
GPIO.setup(12,GPIO.OUT) # Alarm LED ( PWM )

pwmLed = GPIO.PWM(12,1000)	#create PWM instance with frequency
pwmLed.start(0)				#start PWM of required Duty Cycle 

T_SP = 24.5
# print HiveMQTT message
def on_message(client, userdata, msg):
	print(msg.topic + " " + str(msg.qos) + " " + str(msg.payload))
	if msg.topic == 'PID1/SP':
		global T_SP
		T_SP = float(msg.payload)
		print("T_SP " +  str(T_SP))

if __name__ == "__main__":
	Tf = 2 # sec
	Ts = 1 # sec
	PV_AlmLimit = 25
	
	PID1 = PID(Ts, Tf)
	Tmr1 = Tmr(30)  # Update Thingspeak, and 
	Tmr2 = Tmr(2) 	# Print sensor data to console
	Tmr3 = Tmr(10) 	# Update MongoDB Server
	Tmr4 = Tmr(1) 	# PID
	
	# MongoDB Config
	client = pymongo.MongoClient("mongodb://192.168.9.5:27017/")
	database = client["PID1"]
	
	# MQTT Config
	MQTTclient = paho.Client(client_id="", userdata=None, protocol=paho.MQTTv5)
	MQTTclient.on_connect = on_connect
	MQTTclient.tls_set(tls_version=mqtt.client.ssl.PROTOCOL_TLS)
	MQTTclient.username_pw_set("LAB2_PID1", "pw_Lab2_")
	MQTTclient.connect("63b521657cb149749a139c35c8c86af6.s1.eu.hivemq.cloud", 8883)
	MQTTclient.subscribe('PID1/#', qos=1)
	MQTTclient.loop_start()
	
	try:
		while True:
			Tmr1.tmrStart()
			Tmr2.tmrStart()
			Tmr3.tmrStart()
			Tmr4.tmrStart()
			
			PV_AlmLimit = 27
			kp = 0.8
			Ti = 20
			Td = 0
			PID1.config(PV_AlmLimit, Tf, Ts)
			
			MQTTclient.on_connect = on_connect
			MQTTclient.on_subscribe = on_subscribe
			MQTTclient.on_message = on_message
			
			if Tmr1.pulse():
				write_ts_ch('field1',PID1.PV)  
				MQTTclient.publish("PID1/PV", payload=str(PID1.PV), qos=1)

			# Print sensor values
			if Tmr2.pulse():
				print("Pulse 2")
				print("TMP36 Temperature " + str(PID1.PV)+ " Celsius")
				TC74 = bus.read_byte(address)
				print("TC74 Temperature " + str(TC74) + " Celsius")
				pv = PID1.PV
				print("CV: " + str(CV)  + " PV: " + str(pv) + " SP: " + str(T_SP))
				
				
			# Update MongoDB database
			if Tmr3.pulse():
				collection = database["PV"]
				Updt_MongoDB_Srv(PID1.PV, client,database, collection)
				collection = database["CV"]
				Updt_MongoDB_Srv(CV, client,database, collection)
				collection = database["SP"]
				Updt_MongoDB_Srv(T_SP, client,database, collection)
				#printDb(collection)
				#read_ts_ch()
			
			# Update PID controller
			if Tmr4.pulse():
				CV = PID1.PID(TMP36_C(1, 0),T_SP,False,kp,Ti,Td,5,0)
					
			if PID1.almActive() and PID1.PV > PV_AlmLimit:
				pwmLed.ChangeDutyCycle(90) # 0-100%
			elif PID1.almActive() and PID1.PV <= PV_AlmLimit:
				pwmLed.ChangeDutyCycle(25) # 0-100%
			else:
				pwmLed.ChangeDutyCycle(0)
				
			if GPIO.input(20): # Pushbutton
				PID1.ackAlm()
			
	except KeyboardInterrupt:
			MQTTclient.loop_stop()
			MQTTclient.disconnect()
			print("\nKeyboard exit")
