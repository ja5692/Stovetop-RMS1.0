Python 3.5.3 (default, Jan 19 2017, 14:11:04) 
[GCC 6.3.0 20170124] on linux
Type "copyright", "credits" or "license()" for more information.
>>> 
from Hologram.HologramCloud import HologramCloud
import json
import threading
import time
import sys
import Adafruit_DHT
from RPIO import PWM
mintemp = 30 #Minimum temperature required to trigger the "stove on" status
sensor = Adafruit_DHT.DHT11 #Sensor type. 
dhtpin = 4 #GPIO pin the DHT is connected to


credentials = {"devicekey":"2tVU6Pnf"} #Replace with your unique SIM device key
#Instantiating a hologram instance
hologram = HologramCloud(credentials, network='cellular', authentication_type="csrpsk")

result = hologram.network.connect()
print 'CONNECTION STATUS: ' + str(hologram.network.getConnectionStatus())

if result == False:
    print ' Failed to connect to cell network'
else:
    print "Connection successful!"
    print "Hologram online!"
    #Enables Hologram to listen for incoming SMS messages
    recv = hologram.enableSMS()

def update():
    #Log temperature
    humidity, temperature = Adafruit_DHT.read_retry(sensor, dhtpin)
    temperature = float('{0:0.1f}'.format(temperature))

    #Determine if stove is on or off
    if temperature <= mintemp:
        #hologram.sendMessage(json.dumps("Your stove is off." + "Temperature: " + temperature + "C"))
        print "Your stove is off. " + "Temperature: " + str(temperature) + "C"
        reply = hologram.sendSMS(phone, "Your stove is off. " + "Temperature: " + str(temperature) + "C")

    else:
        #hologram.sendMessage(json.dumps("Your stove is on. Your home is at risk, Call authorities " + "Temperature: " + temperature + "C"))
        print "Your stove is on. Your home is at risk, Call authorities " + "Temperature: " + str(temperature) + "C"
        reply = hologram.sendSMS(phone, "Your stove is on. Your home is at risk, Call authorities " + "Temperature:  " + str(temperature) + "C")
        #Waits for and processes user response to prompt
        count = 0
        while True:
            #Reads user response
            sms_obj = hologram.popReceivedSMS()
            if sms_obj is not None:
                message = sms_obj.message.lower()
                if message == "ok":
                    #hologram.sendMessage(json.dumps("Please take necesary action, your home is at risk"))
                    print "Please take necesary action, your home is at risk"
                    reply = hologram.sendSMS(phone, "Please take necesary action, your home is at risk")
                    break

                elif message:
                    #hologram.sendMessage(json.dumps("Please enter a valid response. (ok or ignore)"))
                    print "Please enter a valid response. (ok or ignore)"
                    hologram.sendSMS(phone, "Please enter a valid response. (ok or ignore)")
                    count = 0
                elif count >= 30:
                    #hologram.sendMessage(json.dumps("No response recieved within 30 minutes, Alert Ignored. Reverting to standby mode."))
                    print "No response recieved within 30 seconds, Alert Ignored. Reverting to standby mode."
                    reply = hologram.sendSMS(phone, "No response recieved within 30 seconds, Alert Ignored. Reverting to standby mode.")
                    break
            count += 1
            time.sleep(1)

#Hologram waits for user input (standby mode)
while True:
    sms_obj = hologram.popReceivedSMS()
    if sms_obj is not None: #If user sends something:
        message = sms_obj.message
        phone = "+" + sms_obj.sender

        if message.lower() in "status update": #If user enters keyword
            update()
    time.sleep(1)

hologram.network.disconnect()
