from Hologram.HologramCloud import HologramCloud
import RPi.GPIO as GPIO
import time
import json
import threading
import sys


# change these as desired - they're the pins connected from the
# SPI port on the ADC to the pi
SPICLK = 11
SPIMISO = 9
SPIMOSI = 10
SPICS = 8
smokesensor_dpin = 26
smokesensor_apin = 0

credentials = {"devicekey":"2tVU6Pnf"}    #Replace with your unique SIM device key
                                          #Instantiating a hologram instance
hologram = HologramCloud(credentials, network='cellular', authentication_type="csrpsk")

result = hologram.network.connect()
print 'CONNECTION STATUS: ' + str(hologram.network.getConnectionStatus())

if result == False:
    print ' Failed to connect to cell network'
else:
    print "Connection successful!"
    print "Hologram is online!"
                                           #Enables Hologram to listen for incoming SMS messages
    recv = hologram.enableSMS()


#port init
def init():
         GPIO.setwarnings(False)
         GPIO.cleanup()			#clean up at the end of your script
         GPIO.setmode(GPIO.BCM)		#to specify whilch pin numbering system
         # set up the SPI interface pins
         GPIO.setup(SPIMOSI, GPIO.OUT)
         GPIO.setup(SPIMISO, GPIO.IN)
         GPIO.setup(SPICLK, GPIO.OUT)
         GPIO.setup(SPICS, GPIO.OUT)
         GPIO.setup(smokesensor_dpin,GPIO.IN,pull_up_down=GPIO.PUD_DOWN)

#read SPI data from MCP3008(or MCP3204) chip,8 possible adc's (0 thru 7)
def readadc(adcnum, clockpin, mosipin, misopin, cspin):
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
#main ioop
def main():
         init()
         while True:
                  smokelevel=readadc(smokesensor_apin, SPICLK, SPIMOSI, SPIMISO, SPICS)
                  
                  if GPIO.input(smokesensor_dpin):#hologram.sendMessage(json.dumps("No Gas Leak Detected"))
                           print("No Gas Leak Detected")
                           time.sleep(0.5)
                    break
                  else:
                           print("DANGER!! Gas leakege detected!!")
                  break
                       
                 

                    
while True:
    sms_obj = hologram.popReceivedSMS()
    if sms_obj is not None:                #If user sends something:
        message = sms_obj.message
        phone = "+" + sms_obj.sender

        if message.lower() in "gas": #If user enters keyword
            main()
            break
    time.sleep(1)

GPIO.cleanup()
hologram.network.disconnect()


