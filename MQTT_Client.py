import time
import paho.mqtt.client as paho
from paho import mqtt
import re
from Tmr import *
import numpy as np
import pandas as pd 
import statistics as st
from array import array
import datetime
import matplotlib.pyplot as plt



# setting callbacks for different events to see if it works, print the message etc.
def on_connect(client, userdata, flags, rc, properties=None):
	print("CONNACK received with code %s." % rc)

# with this callback you can see if your publish was successful
def on_publish(client, userdata, mid, properties=None):
	print("mid: " + str(mid))

# print which topic was subscribed to
def on_subscribe(client, userdata, mid, granted_qos, properties=None):
	print("Subscribed: " + str(mid) + " " + str(granted_qos))

PV = list()
SP = list()
t_pv = list()
def on_message(client, userdata, msg):
    #print(msg.topic + " " + str(msg.qos) + " " + str(msg.payload))
    if msg.topic == 'PID1/SP':
        global SP
        SP.append(float(msg.payload))
    if msg.topic == 'PID1/PV':
        global PV
        PV.append(float(msg.payload))
        global t_pv
        t_pv.append(datetime.datetime.now())

          
# MQTT Config
MQTTclient = paho.Client(client_id="", userdata=None, protocol=paho.MQTTv5)
MQTTclient.on_connect = on_connect
MQTTclient.tls_set(tls_version=mqtt.client.ssl.PROTOCOL_TLS)
MQTTclient.username_pw_set("LAB2_PID1", "pw_Lab2_")
MQTTclient.connect("63b521657cb149749a139c35c8c86af6.s1.eu.hivemq.cloud", 8883)
MQTTclient.subscribe('PID1/#', qos=1)

if __name__ == "__main__":
    MQTTclient.loop_start()
    try:
        Tmr1 = Tmr(30)  # Calculate mean etc every 30 sec
        while True:
            Tmr1.tmrStart()
            if Tmr1.pulse():
                if PV:
                    PV_Arr = np.array(PV)
                    t_pv_Arr = np.array(t_pv)
                    PV_df = pd.DataFrame(PV_Arr)
                    Min = min(PV_Arr)
                    print("min temperature is: " + str(Min) + " celsius" )
                    Max = max(PV_Arr)
                    print("Max temperature is: " + str(Max) + " celsius" )
                    Avg = st.mean(PV_Arr)
                    print("Average temperature is: " + str(Avg) + " celsius" )
                    PV_RollingMean = PV_df.rolling(10).mean()
                    plt.plot(t_pv_Arr,PV_Arr, color="blue",label="PV")
                    plt.plot(t_pv_Arr, PV_RollingMean, color="red", label="Rolling Mean PV")
                    plt.title("PV")
                    plt.ylabel("Celsius")
                    plt.legend(loc="best")
                    plt.grid()
                    plt.show()
                    
            MQTTclient.on_connect = on_connect
            MQTTclient.on_subscribe = on_subscribe
            MQTTclient.on_message = on_message
            
    except KeyboardInterrupt:
        MQTTclient.loop_stop()
        MQTTclient.disconnect()
        print("\nKeyboard exit")


