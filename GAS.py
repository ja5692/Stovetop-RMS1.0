#Guidelines used as reference in the implementation of this script**************
#https://hologram.io/docs/reference/cloud/python-sdk/***************************
#https://github.com/hologram-io/hologram-python*********************************
#https://github.com/modular-CAT/python_mq5_gas_sensor***************************
#https://github.com/SeeedDocument/Grove_Gas_Sensor_MQ5/blob/master/Grove_Gas_Sensor_MQ5.md
#*******************************************************************************
#*******************************************************************************
from Hologram.HologramCloud import HologramCloud
import RPi.GPIO as GPIO
import time
import json
import threading
import sys
#*****************************MGP3008 pins**************************************
SPICLK = 11
SPIMISO = 9
SPIMOSI = 10
SPICS = 8
smokesensor_dpin = 26
smokesensor_apin = 0
#*****************************Communication establishment***********************
qualifications = {"devicekey":"2tVU6Pnf"}    
                                          
nova = HologramCloud(qualifications, network='cellular', authentication_type="csrpsk")
outcome = nova.network.connect()
print 'ESTABLISHING COMMUNICATION:' + str(nova.network.getConnectionStatus())

if outcome == False:
    print 'FAILED TO ESTABLISH CONNECTION'
else:
    print "CONNECTION ESTABLISHED"
    print "GSM MODULE IS CONECTED TO NETWORK!"
                                          
    recv = nova.enableSMS()


#****************************Ports cleaning and setup ***************************
def port():
         GPIO.setwarnings(False)
         GPIO.cleanup()			    
         GPIO.setmode(GPIO.BCM)		
                                   
         GPIO.setup(SPIMOSI, GPIO.OUT)
         GPIO.setup(SPIMISO, GPIO.IN)
         GPIO.setup(SPICLK, GPIO.OUT)
         GPIO.setup(SPICS, GPIO.OUT)
         GPIO.setup(smokesensor_dpin,GPIO.IN,pull_up_down=GPIO.PUD_DOWN)

#**************************data reading from the MGp3008************************
def mgpread(adcnum, clockpin, mosipin, misopin, cspin):
        if ((adcnum > 7) or (adcnum < 0)):
                return -1
        GPIO.output(cspin, True)	

        GPIO.output(clockpin, False) 
        GPIO.output(cspin, False)    

        commandout = adcnum
        commandout |= 0x18  
        commandout <<= 3   
        for i in range(5):
                if (commandout & 0x80):
                        GPIO.output(mosipin, True)
                else:
                        GPIO.output(mosipin, False)
                commandout <<= 1
                GPIO.output(clockpin, True)
                GPIO.output(clockpin, False)

        adcout = 0
        
        for i in range(12):
                GPIO.output(clockpin, True)
                GPIO.output(clockpin, False)
                adcout <<= 1
                if (GPIO.input(misopin)):
                        adcout |= 0x1

        GPIO.output(cspin, True)
        
        adcout >>= 1       
        return adcout
#********************************Alerting**************************************
def mq5():
         port()
         while True:
                  smokelevel=adcread(analog_pin, SPICLK, SPIMOSI, SPIMISO, SPICS)
                  
                  if GPIO.input(smokesensor_dpin):
                           print("DANGER!! Gas/smoke detected!!)
                           reply = nova.sendSMS(phone, "No Gas/smoke Detected")
                           time.sleep(0.5)
                  else:
                           print("DANGER!! Gas/smoke detected!!")
                           reply = nova.sendSMS(phone, "DANGER!! Gas / smoke detected!!")
                           break
                  count = 1
                  time.sleep(1)
                  quit()

                    
while True:
    sms_obj = nova.popReceivedSMS()
    if sms_obj is not None:         
        message = sms_obj.message
        phone = "+" + sms_obj.sender

        if response.lower() in "gas":
            mq5()
            
    time.sleep(1)

nova.network.disconnect()
GPIO.cleanup()
