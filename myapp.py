
#importing the libraries that are needed from the iothub_client library
#This is the library for  communicating with the IOT hub on Azure
from iothub_client import IoTHubClient, IoTHubClientError, IoTHubTransportProvider, IoTHubClientResult
from iothub_client import IoTHubMessage, IoTHubMessageDispositionResult, IoTHubError, DeviceMethodReturnValue
import RPi.GPIO as GPIO
import sys,re
import math
#Import the firmware code from the Adafruit BM280 temp and humidity sensor
from Adafruit_BME280 import *

#import the telemetry class which allows communication with iothubclient
from telemetry import Telemetry

#Import the firmware code for the Adafruit MAX31855 Amplifier for the Thermocouple
import Adafruit_MAX31855.MAX31855 as MAX31855

#import smbus for use with the DHT20 sensor and setting up the bus with the address
import smbus
import time
bus = smbus.SMBus(1)
#SHT20 address, 0x40(64)

#import MCP3008 (ADC) Library 
import Adafruit_MCP3008

#importing the DHT11 sensor library
import Adafruit_DHT

#Setting the variables needed for the Current sensor code
vRMS = 120.0
offset = 2.5
numTurns = 2000
rBurden = 150.0
numSamples = 1000
compRunning = False
startTime = 0
globalTimeOn = 0
endTime = 0

#creating DHT sensor object
DHTsensor = Adafruit_DHT.DHT22

#Configuring SPI Software for the Adafruit_MCP3008 ADC. These are the GPIO numbers
CLK_mcp = 25
MISO_mcp = 23
MOSI_mcp = 24
CS_mcp = 18
mcp = Adafruit_MCP3008.MCP3008(clk=CLK_mcp, cs=CS_mcp, miso=MISO_mcp, mosi=MOSI_mcp)


#configuring the SPI software for the MAX31855 Amplifier for the Thermocouple
CLK_max = 6
CS_max  = 13
DO_max  = 26
max_sensor = MAX31855.MAX31855(CLK_max, CS_max, DO_max)



#configure pin for Adafruit_DHT11 Sensor
DHTpin = 21


#Making a telemetry object which will allow this computer to communicate with IotHub
telemetry = Telemetry()

#pin number for LED 
LED_PIN_ADDRESS = 12

MESSAGE_COUNT = 0
MESSAGE_SWITCH = True

# global counters
RECEIVE_CALLBACKS = 0
SEND_CALLBACKS = 0
RECEIVE_CONTEXT = 0
SEND_REPORTED_STATE_CALLBACKS = 0

#set the connection string variable as the 2nd parameter that was passed into the application call (i.e. "python app.py  [connection string]"")
CONNECTION_STRING = 'HostName=GastNitroGenHub.azure-devices.net;DeviceId=NitroGenDeviceID;SharedAccessKey=gZ6QBszztg3zCc5afoDI0cg4nhlDCgZD0vMYPDpMvU0='

#Using the MQTT protocol for sending messages. 
#It is a lightweight messaging protocol for small devices and sensors
PROTOCOL = IoTHubTransportProvider.MQTT

#Set the mode for the raspberry pi to use the pin number (GPIO.BCM). also setting the output pin for the LED
GPIO.setmode(GPIO.BCM)
GPIO.setup(LED_PIN_ADDRESS, GPIO.OUT)


#this is the message text variable that gets sent to the IOT hub after being formatted with the respective variables
MSG_TXT = "{\"deviceId\": \"Raspberry Pi - Python\",\"compState\": %f , \"bme280Temperature\": %f,\"bme280Humidity\": %f ,\"bme280Pressure\": %f ,\"thermocoupleTemperature\": %f,\"sht20Temperature\": %f,\"sht20Humidity\": %f,\"transducerPressure\": %f,\"am2302Pressure\": %f,\"am2302Humidity\": %f}"

#not too sure about this method yet. I think it recieves data from the IOT hub as a confirmation that the data was recieved
def receive_message_callback(message, counter):
    global RECEIVE_CALLBACKS
    message_buffer = message.get_bytearray()
    size = len(message_buffer)
    print ( "Received Message [%d]:" % counter )
    print ( "    Data: <<<%s>>> & Size=%d" % (message_buffer[:size].decode("utf-8"), size) )
    map_properties = message.properties()
    key_value_pair = map_properties.get_internals()
    print ( "    Properties: %s" % key_value_pair )
    counter += 1
    RECEIVE_CALLBACKS += 1
    print ( "    Total calls received: %d" % RECEIVE_CALLBACKS )
    return IoTHubMessageDispositionResult.ACCEPTED

#Simple method for sending text to the terminal signifying that a confirmation was recieved with the data passed into it
def send_reported_state_callback(status_code, user_context):
    global SEND_REPORTED_STATE_CALLBACKS
    print ( "Confirmation for reported state received with:\nstatus_code = [%d]\ncontext = %s" % (status_code, user_context) )
    SEND_REPORTED_STATE_CALLBACKS += 1
    print ( "    Total calls confirmed: %d" % SEND_REPORTED_STATE_CALLBACKS )

#This is the function that send that information back to the terminal that the app is being run from. The led blinks every time that this method is called
# and completed successfully.
def send_confirmation_callback(message, result, user_context):
    global SEND_CALLBACKS
    print ( "Confirmation[%d] received for message with result = %s" % (user_context, result) )
    map_properties = message.properties()
    print ( "    message_id: %s" % message.message_id )
    print ( "    correlation_id: %s" % message.correlation_id )
    key_value_pair = map_properties.get_internals()
    print ( "    Properties: %s" % key_value_pair )
    SEND_CALLBACKS += 1
    print ( "    Total calls confirmed: %d" % SEND_CALLBACKS )
    led_blink()


def iothub_client_init():
    #prepare the iothub client (basically the iot hub on azure)
    client = IoTHubClient(CONNECTION_STRING,PROTOCOL)
    client.set_option("product_info", "HappyPath_RaspberryPi-Python")
    client.set_option("Message Time Out", 10000 )
    if client.protocol == IoTHubTransportProvider.MQTT:
        client.set_option("logtrace",0)
    client.set_message_callback(receive_message_callback, RECEIVE_CONTEXT)
    return client

def print_last_message_time(client):
    try:
        last_message = client.get_last_message_receive_time()
        print ( "Last Message: %s" % time.asctime(time.localtime(last_message)) )
        print ( "Actual time : %s" % time.asctime() )
    except IoTHubClientError as iothub_client_error:
        if iothub_client_error.args[0].result == IoTHubClientResult.INDEFINITE_TIME:
            print ( "No message received" )
        else:
            print ( iothub_client_error )

def iothub_client_sample_run():
    global compRunning
    global globalTimeOn
    try:
        client = iothub_client_init()
        if client.protocol == IoTHubTransportProvider.MQTT:
            print ( "IoTHubClient is reporting state" )
            reported_state = "{\"newState\":\"standBy\"}"
            client.send_reported_state(reported_state, len(reported_state), send_reported_state_callback, 0)
        bme280Sensor = BME280(address= 0x77)
        telemetry.send_telemetry_data(parse_iot_hub_name,"success", "The connection to the IOT Hub has been established!!!...Boom")
        while True:
            global MESSAGE_COUNT, MESSAGE_SWITCH
            if MESSAGE_SWITCH:
                print ( "IoTHubClient sending %d messages...boom" % MESSAGE_COUNT )
                compState = CheckCompressorState()
                #reading data from sensors and formatting messages to be sent to client(iotHub)
                thermocoupleTemperature = c_to_f(max_sensor.readTempC())
                sht20Temperature = GetShtTemp_f()
                sht20Humidity = GetShtHumid()
                bme280Temperature = bme280Sensor.read_temperature_f()
                bme280Humidity = bme280Sensor.read_humidity()
		am2302Humidity,am2302Pressure = Adafruit_DHT.read_retry(DHTsensor,DHTpin)
		bme280Pressure = bme280Sensor.read_pressure()
                transducerPressure  = (mcp.read_adc(7)-75)*150.0/835.0
                msg_text_formatted = MSG_TXT %(compState,bme280Temperature,bme280Humidity,bme280Pressure,thermocoupleTemperature,sht20Temperature,sht20Humidity,transducerPressure,am2302Pressure,am2302Humidity)
                print(msg_text_formatted)
                message = IoTHubMessage(msg_text_formatted)
                

                #mapping extra properties for the message. basically just adding a temperature warning
                prop_map = message.properties()
                prop_map.add("TemperatureAlert..boom","true" if bme280Temperature > 30.0 else "false")

                #sending the message to the terminal from iotHub
                client.send_event_async(message,send_confirmation_callback,MESSAGE_COUNT)
                print ( "IoTHubClient.send_event_async accepted message [%d] for transmission to IoT Hub." % MESSAGE_COUNT )
                
                #sending  the send status to the terminal from the iotHub
                status = client.get_send_status()
                print("Send status is..boom... %s" % status)
                MESSAGE_COUNT +=1
            if compRunning == True:
                globalTimeOn += 2.0
            time.sleep(2)

    except IoTHubError as iothub_error:
        print ( "Unexpected error %s from IoTHub" % iothub_error )
        telemetry.send_telemetry_data(parse_iot_hub_name(), "failed", "Unexpected error %s from IoTHub" % iothub_error)
        return
    except KeyboardInterrupt:
        print ( "IoTHubClient sample stopped" )
        print(globalTimeOn)
        
#Method to get the temperature data from the DHT20 sensor
def GetShtTemp_f():
    global compRunning
    global globalTimeOn
    # Send temperature measurement command
    #		0xF3(243)	NO HOLD master
    bus.write_byte(0x40, 0xF3)
    if compRunning == True:
        globalTimeOn += 0.5
    time.sleep(0.5)
    shtData0 = bus.read_byte(0x40)
    shtData1 = bus.read_byte(0x40)
    # Convert the data
    temp = shtData0 * 256 + shtData1
    cTemp= -46.85 + ((temp * 175.72) / 65536.0)
    fTemp = cTemp * 1.8 + 32
    return fTemp

#Method to get the temperature data from the DHT20 sensor
def GetShtTemp_c():
    global compRunning
    global globalTimeOn
    # Send temperature measurement command
    #		0xF3(243)	NO HOLD master
    bus.write_byte(0x40, 0xF3)
    if compRunning == True:
        globalTimeOn += 0.5
    time.sleep(0.5)
    shtData0 = bus.read_byte(0x40)
    shtData1 = bus.read_byte(0x40)
    # Convert the data
    temp = shtData0 * 256 + shtData1
    cTemp= -46.85 + ((temp * 175.72) / 65536.0)
    return cTemp
        
#Method to get the humidity data from the DHT20 sensor
def GetShtHumid():
    global compRunning
    global globalTimeOn
    # SHT25 address, 0x40(64)
    # Send humidity measurement command
    #		0xF5(245)	NO HOLD master
    bus.write_byte(0x40, 0xF5)
    if compRunning == True:
        globalTimeOn += 0.5
    time.sleep(0.5)

    # SHT25 address, 0x40(64)
    # Read data back, 2 bytes
    # Humidity MSB, Humidity LSB
    shtData0 = bus.read_byte(0x40)
    shtData1 = bus.read_byte(0x40)

    # Convert the data
    shtHumidity = shtData0 * 256 + shtData1
    shtHumidity = -6 + ((shtHumidity * 125.0) / 65536.0)
    return shtHumidity


#method to get the LED to blink for a specified amount of time
def led_blink():
    global compRunning
    global globalTimeOn
    GPIO.output(LED_PIN_ADDRESS,GPIO.HIGH)
    if compRunning == True:
        globalTimeOn += 1
    time.sleep(1) #the time that the LED stays lit for
    GPIO.output(LED_PIN_ADDRESS, GPIO.LOW)

#self explanatory method
def parse_iot_hub_name():
    m = re.search("HostName=(.*?)\.", CONNECTION_STRING)
    return m.group(1)

#Method to convert from celcius to farenheit
def c_to_f(c):
        return c * 9.0 / 5.0 + 32.0

    
def CheckCompressorState():
    global globalTimeOn
    global compRunning
    global startTime
    acc = 0.00
    for i in range(numSamples):
        sample = mcp.read_adc(6)
        voltage = (float(sample)*5.0)/1023
        voltage = voltage-offset
        iPrimary = (voltage/rBurden)*numTurns
        acc += (iPrimary*iPrimary)
    iRMS = math.sqrt(acc/numSamples)
    if iRMS > .25 and compRunning == False:
        compRunning = True
        startTime = time.time()
    elif iRMS > .25 and compRunning == True:
        timeElapsed = time.time() - startTime
        startTime = time.time()
        globalTimeOn += timeElapsed
    elif iRMS <.25 and compRunning == True:
        timeElapsed = time.time() - startTime
        globalTimeOn += timeElapsed
        compRunning = False
    if compRunning == True:
        return 1
    else:
        return 0

if __name__ == "__main__":
    print("\nPython %s" % sys.version)
    print(" IoT Hub Client for Python")
    iothub_client_sample_run()
