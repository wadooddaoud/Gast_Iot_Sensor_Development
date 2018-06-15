# Simple example of reading the MCP3008 analog input channels and printing
# them all out.
# Author: Tony DiCola
# License: Public Domain
import time
import math

# Import SPI library (for hardware SPI) and MCP3008 library.
import Adafruit_GPIO.SPI as SPI
import Adafruit_MCP3008

vRMS = 120.0
offset = 2.5
numTurns = 2000
rBurden = 150.0
numSamples = 1000
compRunning = False
startTime = 0
globalTimeOn = 0
endTime = 0


# Software SPI configuration:
CLK  = 25
MISO = 23
MOSI = 24
CS   = 18
mcp = Adafruit_MCP3008.MCP3008(clk=CLK, cs=CS, miso=MISO, mosi=MOSI)

print("-------")
print('Reading MCP3008 values for the Current sensor')

# Main program loop.
for w in range(75):
    acc = 0.00
    for i in range(numSamples):
        sample = mcp.read_adc(6)
        voltage = (float(sample)*5.0)/1023
        voltage = voltage-offset
        iPrimary = (voltage/rBurden)*numTurns
        acc += (iPrimary*iPrimary)
    iRMS = math.sqrt(acc/numSamples)
    print("this is the Irms Amperage in Amps:")
    print(iRMS)
    if iRMS > .25 and compRunning == False:
        compRunning = True
        startTime = time.time()
    elif iRMS <.25 and compRunning ==True:
        timeElapsed = time.time() - startTime
        globalTimeOn += timeElapsed
        compRunning = False
        
    #apparentPower = vRMS*iRMS
    #print(" this is the apparent power in Volt Amps")
    #print(apparentPower)
    #time.sleep(10)
    print("----------")
print("The total time it was on is")
print(globalTimeOn)