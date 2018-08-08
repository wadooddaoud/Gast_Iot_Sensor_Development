import time
#time.sleep(20)
#importing the libraries that are needed from the iothub_client library
#This is the library for  communicating with the IOT hub on Azure
from iothub_client import IoTHubClient, IoTHubClientError, IoTHubTransportProvider, IoTHubClientResult
from iothub_client import IoTHubMessage, IoTHubMessageDispositionResult, IoTHubError, DeviceMethodReturnValue

#Importing the hologram nova cloud library which allows us to leverage hologram's cellular network
from Hologram.HologramCloud import HologramCloud

#import the raspberry pi GPIO library which allows you to access the GPIO (General Input/Output) pins of the raspberry pi
import RPi.GPIO as GPIO

# These are imports for libraries that are virtually consistent across all python code. sys is to interact with the system, re is a library for regular expressions,
# and numpy is for mathematical functions within, but not limited to, arrays
import sys,re
import math
import numpy as np

#import the telemetry class which allows communication with iothubclient. Telemetry is basically the eyes and ears of the IoT device. We use the telemetry module to
# connect to the IoT Hub
from telemetry import Telemetry

#Import the firmware code for the Adafruit MAX31855 Amplifier for the Thermocouple
import Adafruit_MAX31855.MAX31855 as MAX31855


#import MCP3008 (ADC) Library 
import Adafruit_MCP3008

#importing the DHT11 sensor library
import Adafruit_DHT

# the first command creates an object which allows connection to the hologram cloud. The next command actually initalizes a connection to the hologram cloud.
#hologram = HologramCloud(dict(), network='cellular')
#result = hologram.network.connect()



#Setting the variable for the max length of the arrays storing data
# We only madethe am2302 humidity array to mitigate errors within the sensor readings
MAX_ARRAY_LENGTH = 50
am2302HumidityArray = []


  
#Setting the variables needed for the Current sensor code. A lot of these numbers correlate to math that was carried out to define the voltage divider and burden sensor to provide
#accurate current sensor readings
vRMS = 120.0
offset = 2.5
numTurns = 2000
rBurden = 150.0
numSamples = 1000
compRunning = False
startTime = 0
globalTimeOn = 0
endTime = 0
dutyCycleArray = []

#creating DHT sensor object
DHTsensor = Adafruit_DHT.DHT22

#Configuring SPI Software for the Adafruit_MCP3008 ADC. These are the GPIO numbers
CLK_mcp = 22
MISO_mcp = 23
MOSI_mcp = 24
CS_mcp = 25
mcp = Adafruit_MCP3008.MCP3008(clk=CLK_mcp, cs=CS_mcp, miso=MISO_mcp, mosi=MOSI_mcp)


#configuring the SPI software for the MAX31855 Amplifier for the Thermocouple
CLK_max = 21
CS_max  = 20
DO_max  = 16
max_sensor = MAX31855.MAX31855(CLK_max, CS_max, DO_max)

#configure pin for Adafruit_DHT11 Sensor
DHTpin = 4

#pin number for LED 
LED_PIN_ADDRESS = 17

#Making a telemetry object which will allow this computer to initialize a connections with the IotHub
telemetry = Telemetry()

MESSAGE_COUNT = 0
MESSAGE_SWITCH = True

# global counters
RECEIVE_CALLBACKS = 0
SEND_CALLBACKS = 0
RECEIVE_CONTEXT = 0
SEND_REPORTED_STATE_CALLBACKS = 0

# These are the connection strings that allow for the IoT Device to be authenticated with the IoT Hub. The shared access key is critical to the IoT hub allowing a connection and can
# be found on the IoT hub under the devices ---> "connection string primary".
CONNECTION_STRING_NITRO = 'HostName=GastNitroGenHub.azure-devices.net;DeviceId=NitroGenCellular;SharedAccessKey=F/cqWVnYF/k6hRQnxV/X7a9IP/FzF6ibV5HRSJ2PDAw='
#CONNECTION_STRING_NITRO = 'HostName=JA-TestProject.azure-devices.net;DeviceId=RasBerryOnlineTestBoard;SharedAccessKey=56PL8iS1Pb2i5SE2Qke8CXXIRLgmCwJVHL+CLauuW1o='

#Using the MQTT protocol for sending messages. 
#It is a lightweight messaging protocol for small devices and sensors
PROTOCOL = IoTHubTransportProvider.MQTT

#Set the mode for the raspberry pi to use the pin number (GPIO.BCM). also setting the output pin for the LED
GPIO.setmode(GPIO.BCM)
GPIO.setup(LED_PIN_ADDRESS, GPIO.OUT)


#this is the message text variable that gets sent to the IOT hub after being formatted with the respective variables
MSG_TXT = "{\"deviceId\": \"NitroGenCellular\", \"nitroGen\": %f,\"timeEpoch\": %f, \"globalTimeOn\": %f,\"dutyCycle\": %f,\"compState\": %f ,\"thermTemp\": %f,\"transPres\": %f,\"ambTemp\": %f,\"ambHum\": %f}"
#MSG_TXT = "{\"deviceId\": \"JunAir 1.0\", \"nitroGeneration\": %f,\"timeEpoch\": %f, \"globalTimeOn\": %f,\"dutyCycle\": %f,\"compState\": %f ,\"thermocoupleTemperature\": %f,\"transducerPressure\": %f,\"am2302Temperature\": %f,\"am2302Humidity\": %f"


#This method is from Azure and it is printed in the IoT hub terminal and drives the messages that are recieved back from the IoT Hub which confirms that a message was recieved.
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

#Simple method for sending text to the terminal of the IoT Hub signifying that a confirmation was recieved at the IoT hub with the data passed into it
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

# Initializes an IoT Hub client which we use to handle our messages. This client gives a direct connection to the IoT hub as it contains the connection string for the device in use and
# the communication protocol to be used with the IoT Hub
def iothub_client_init(CONNECTION_STRING_GIVEN, PROTOCOL):
    #prepare the iothub client (basically the iot hub on azure)
    client = IoTHubClient(CONNECTION_STRING_GIVEN,PROTOCOL)
    client.set_option("product_info", "HappyPath_RaspberryPi-Python")
    client.set_option("Message Time Out", 10000 )
    if client.protocol == IoTHubTransportProvider.MQTT:
        client.set_option("logtrace",0)
    client.set_message_callback(receive_message_callback, RECEIVE_CONTEXT)
    return client


#Method that sends text to the IoT hub terminal to show the time between messages. This time is also another way that the IoT hub authenticats the messages as the messages should be coming from a
# similar time zone
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

# Main method where all of the sensor methods are called and all of the messages are actually created and sent to the Iot Hub.
def iothub_client_sample_run():
    led_blink()
    global compRunning
    global globalTimeOn
    global dutyCycleArray
    global am2302HumidityArray
    try:
        client_nitro = iothub_client_init(CONNECTION_STRING_NITRO, PROTOCOL)
        if client_nitro.protocol == IoTHubTransportProvider.MQTT:
            print ( "IoTHubClient is reporting state" )
            reported_state = "{\"newState\":\"standBy\"}"
            client_nitro.send_reported_state(reported_state, len(reported_state), send_reported_state_callback, 0)
        telemetry.send_telemetry_data(parse_iot_hub_name,"success", "The connection to the IOT Hub has been established!")
        while True:
            global MESSAGE_COUNT, MESSAGE_SWITCH
            if MESSAGE_SWITCH:
                print ( "IoTHubClient sending %d messages" % MESSAGE_COUNT )
                #reading data from sensors and formatting messages to be sent to client(iotHub)
                thermocoupleTemperature = c_to_f(max_sensor.readTempC())
		am2302Humidity,am2302Temperature = Adafruit_DHT.read_retry(DHTsensor,DHTpin)
		if am2302Humidity > 100:
                    am2302Humidity = sum(am2302HumidityArray)/float(len(am2302HumidityArray))
                if len(am2302HumidityArray) > 100:
                    am2302HumidityArray = am2302HumidityArray[1:50]
		am2302HumidityArray.append(am2302Humidity)
		# added .0000001 to transducerPressure because webapp doesnt update with zero
                transducerPressure  = ((mcp.read_adc(0)-72)*150.0/595.2)+ .000001
                compState = CheckCompressorState()
                dutyCycleArray.append(compState)
                dutyCycle = calculateDutyCycle()*100
		timeEpoch = int(time.time())
                if len(dutyCycleArray) > 200:
                    dutyCycleArray = dutyCycleArray[1:150]
                    
                # This code below takes the data obtained from the Excel sheet named "LR-AP067-078.xls" and correlates duty cycle to nitrogen generated per second by the E7   
                averageDutyCycle = 0.32816666667
                averageSecondsPer1scf = (averageDutyCycle * 60*60)/6
                averageNitroGenPerSec = 1/averageSecondsPer1scf
                # added .0000001 to nitroGeneration because webapp doesnt update with zero
                nitroGeneration = (globalTimeOn * averageNitroGenPerSec)+ .000001
                
                #The next lines of code deal with adding the variables to the MSG_TXT varialbe above and sending that message to the IoT hub client specified earlier in the document.
                msg_text_formatted = MSG_TXT %(nitroGeneration,timeEpoch,globalTimeOn,dutyCycle,compState,thermocoupleTemperature,transducerPressure,c_to_f(am2302Temperature),am2302Humidity)
                print(msg_text_formatted)
                message = IoTHubMessage(msg_text_formatted)
                # optional: assign ids
                message.message_id = "message_%d" % MESSAGE_COUNT
                message.correlation_id = "correlation_%d" % MESSAGE_COUNT
                #mapping extra properties for the message. basically just adding a temperature warning
                prop_map = message.properties()
                prop_map.add("TemperatureAlert... ","true" if thermocoupleTemperature > 120.0 else "false")

                #sending the message to the terminal from iotHub
                client_nitro.send_event_async(message,send_confirmation_callback,MESSAGE_COUNT)
                #client_junair.send_event_async(message,send_confirmation_callback,MESSAGE_COUNT)
                print ( "IoTHubClient.send_event_async accepted message [%d] for transmission to IoT Hub." % MESSAGE_COUNT )
                
                #sending  the send status to the terminal from the iotHub
                status_nitro = client_nitro.get_send_status()
                #status_junair = client_nitro.get_send_status()
                print("Send status is... %s" % status_nitro)
                #print("Send status is... %s" % status_junair)
                MESSAGE_COUNT +=1
            time.sleep(2)

    except IoTHubError as iothub_error:
        print ( "Unexpected error %s from IoTHub" % iothub_error )
        telemetry.send_telemetry_data(parse_iot_hub_name(), "failed", "Unexpected error %s from IoTHub" % iothub_error)
        return
    except KeyboardInterrupt:
        print ( "IoTHubClient sample stopped" )


#method to get the LED to blink for a specified amount of time
def led_blink():
    global compRunning
    global globalTimeOn
    GPIO.output(LED_PIN_ADDRESS,GPIO.HIGH)
    time.sleep(1)
    GPIO.output(LED_PIN_ADDRESS, GPIO.LOW)

#self explanatory method
def parse_iot_hub_name():
    m = re.search("HostName=(.*?)\.", CONNECTION_STRING)
    return m.group(1)

#Method to convert from celcius to farenheit
def c_to_f(c):
        return c * 9.0 / 5.0 + 32.0

# This method checks the state of the compressor by checking if there is an amperage draw above 0.40. This value was chosen because the "home" state of the current transformer is about
# 0.20 so anything about 0.40 should be on. The globalTimeOn varialbe this is used to calculate the nitrogen generation by the system is also updated in this method.
def CheckCompressorState():
    global globalTimeOn
    global compRunning
    global startTime
    acc = 0.00
    for i in range(numSamples):
        sample = mcp.read_adc(1)
        voltage = (float(sample)*5.0)/1023
        voltage = voltage-offset
        iPrimary = (voltage/rBurden)*numTurns
        acc += (iPrimary*iPrimary)
    iRMS = math.sqrt(acc/numSamples)
    if iRMS > .40 and compRunning == False:
        compRunning = True
        startTime = time.time()
    elif iRMS > .40 and compRunning == True:
        timeElapsed = time.time() - startTime
        startTime = time.time()
        globalTimeOn += timeElapsed
    elif iRMS <.40 and compRunning == True:
        timeElapsed = time.time() - startTime
        globalTimeOn += timeElapsed
        compRunning = False

    if compRunning == True:
        return 1
    else:
        return 0

#calculates the duty cycle of the device by checking how many times the compressor was on within a run.
def calculateDutyCycle():
    global dutyCycleArray
    y = np.array(dutyCycleArray)
    num_ones = (y == 1).sum()
    return (float(num_ones)/len(y))


if __name__ == "__main__":
    print("\nPython %s" % sys.version)
    print(" IoT Hub Client for Python")
    iothub_client_sample_run()
