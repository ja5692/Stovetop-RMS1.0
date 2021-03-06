#Guidelines used as reference in the implementation of this script**************
#https://hologram.io/docs/reference/cloud/python-sdk/***************************
#https://github.com/hologram-io/hologram-python*********************************
#*******************************************************************************
from Hologram.HologramCloud import HologramCloud
import threading
import time
import sys
import json         #used to store and communicate information to other products
import Adafruit_DHT #sensor library
#*******************************************************************************
pin = 4 
tempthreshold = 35                           
tempsensor = Adafruit_DHT.DHT11              
                               
#*After establishing Connection Hologram will listen for messages until stopped*

qualifications = {"devicekey":"2tVU6Pnf"}   
                                         
nova = HologramCloud(qualifications, network='cellular', authentication_type="csrpsk")

outcome = nova.network.connect()
print 'CONNECTION STATUS: ' + str(nova.network.getConnectionStatus())

if outcome == False:
    print "FAILED TO CONNECT TO NETWORK"
else:
    print "CONNECTION ESTABLISHED"
    print "GSM MODULE CONNECTED TO NETWORK"
                                          
    recv = nova.enableSMS()
#***********************Stove on or off Differenciation*************************
def rms():
  
    tempreading = Adafruit_DHT.read_retry(tempsensor, pin)
    tempreading = float('{0:0.1f}'.format(tempreading))
                          
    if tempreading <= tempthreshold:
                                           
        print "STOVE IS OFF " + "TEMPERATURE DETECTED:" + str(tempreading) + "C"
        reply = nova.sendSMS(phone, "STOVE IS OFF" + "TEMPERATURE: " + str(tempreading) + "C" "YOUR HOME IS SAFE"+ " No Smoke/Gas Detected")

    else:
                                           
        print "STOVE IS ON. YOUR HOME IS AT RISK. PLEASE CONFIRM THIS ALERT HAS BEEN RECIEVED " + "TEMPERATURE: " + str(tempreading) + "C"
        reply = nova.sendSMS(phone, "STOVE IS ON. YOUR HOME IS AT RISK. " + "TEMPERATURE:  " + str(tempreading) + "C" + " Smoke/Gas Detected" )
                                           
        count = 0
        while True:
                                           
            sms_obj = nova.popReceivedSMS()
            if sms_obj is not None:
                response = sms_obj.message.lower()
                
                if response == "ok":
                                           
                    print "ALERT CONFIRMED, TAKE NECESARY MEASURES, YOUR HOME IS AT RISK"
                    reply = nova.sendSMS(phone, "ALERT CONFIRMED, TAKE NECESARY MEASURES, YOUR HOME IS AT RISK")
                    break
                        
                elif count >= 10:
                                           
                    print "NO RESPONSE WAS RECIEVED AFTER 10 MINUTES, ALERT IGNORED."
                    reply = nova.sendSMS(phone, "NO RESPONSE WAS RECIEVED AFTER 10 MINUTES, ALERT IGNORED..RETURNING TO STANDBY.")
                    break
            count += 1
            time.sleep(1)
#************************Nova interaction with user*****************************
while True:
    sms_obj = nova.popReceivedSMS()
    if sms_obj is not None:                
        message = sms_obj.message
        phone = "+" + sms_obj.sender

        if message.lower() in "stove": 
            rms()
    time.sleep(1)

nova.network.disconnect()
