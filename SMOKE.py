#Guidelines used as reference in the implementation of this script**************
#https://hologram.io/docs/reference/cloud/python-sdk/***************************
#https://github.com/hologram-io/hologram-python*********************************
#*******************************************************************************
from Hologram.HologramCloud import HologramCloud
import threading
from threading import Thread
import RPi.GPIO as GPIO
import time
import sys
import json         #used to store and communicate information to other products
import Adafruit_DHT #sensor library
#*******************************************************************************
CLK = 11
MISO = 9
MOSI = 10
CS = 8
digital_dpin = 26
analog_apin = 0
pin = 4 
tempthreshold = 22                           
tempsensor = Adafruit_DHT.DHT11              
                               
#****************************COMMUNICATION ESTABLISHMENT*************************
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
#****************************Ports cleaning and setup ****************************
def init():
         GPIO.setwarnings(False)
         GPIO.cleanup()			      #port cleaning
         GPIO.setmode(GPIO.BCM)		
         # set up the SPI interface pins
         GPIO.setup(MOSI, GPIO.OUT)
         GPIO.setup(MISO, GPIO.IN)
         GPIO.setup(CLK, GPIO.OUT)
         GPIO.setup(CS, GPIO.OUT)
         GPIO.setup(digital_dpin,GPIO.IN,pull_up_down=GPIO.PUD_DOWN)

#Data reading and interpretation from MCP3008 analog to digital converter ********
def mcpread(adcnum, clockpin, mosipin, misopin, cspin):
        if ((adcnum > 7) or (adcnum < 0)):
                return -1
        GPIO.output(cspin, True)	

        GPIO.output(clockpin, False)  # start clock low
        GPIO.output(cspin, False)     # bring CS low

        commandout = adcnum
        commandout |= 0x18  # start bit + single-ended bit
        commandout <<= 3    # we only need to send 5 bits here
        for i in range(5):
                if (commandout & 0x80):
                        GPIO.output(mosipin, True)
                else:
                        GPIO.output(mosipin, False)
                commandout <<= 1
                GPIO.output(clockpin, True)
                GPIO.output(clockpin, False)

        adcout = 0
        # read in one empty bit, one null bit and 10 ADC bits
        for i in range(12):
                GPIO.output(clockpin, True)
                GPIO.output(clockpin, False)
                adcout <<= 1
                if (GPIO.input(misopin)):
                        adcout |= 0x1

        GPIO.output(cspin, True)
        
        adcout >>= 1       # first bit is 'null' so drop it
        return adcout
#*******************************************************************************
#***********************Stove and gas on or off Differenciation*************************
def rms():
  
    humidity, temperature = Adafruit_DHT.read_retry(tempsensor, pin)
    temperature = float('{0:0.1f}'.format(temperature))
                          
    if temperature <= tempthreshold:
                                           
        print "STOVE IS OFF " + "TEMPERATURE DETECTED:" + str(temperature ) + "C"
        
    else:
                                           
        print "STOVE IS ON. YOUR HOME IS AT RISK. " + "TEMPERATURE: " + str(temperature ) + "C"
        
                                           
        count = 0
        while True:
                                           
            sms_obj = nova.popReceivedSMS()
            if sms_obj is not None:
                response = sms_obj.message.lower()
                
               
                        
            elif count >= 10:
                                           
                print "STOVE IS ON, YOUR HOME IS IN DANGER!."
                    
                break
            count += 1
            time.sleep(1)
            
            
            
def mq5():
         init()
         while True:
                  smokelevel=readadc(analog_apin, CLK, MOSI, MISO, CS)
                  
                  if GPIO.input(digital_dpin):
                           print("No Gas/smoke Detected, Your home is safe")
                           
                           time.sleep(0.5)
                  else:
                           print("DANGER!! Gas/smoke detected!!")
                           
                           break
                  count = 2
                  time.sleep(1)
                  quit()
                  
#************************Nova interaction with user*****************************
if __name__ == '__main__':
    Thread(target = mq5).start()
    Thread(target = rms).start()
nova.network.disconnect()
