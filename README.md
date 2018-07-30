# MAX 31855 Thermocouple Amplifier

Python code to use the MAX 31855 thermocouple amplifier with a raspberry pi

# Installing Dependencies
To install the dependencies, run the following commands in the raspberry pi terminal

     sudo apt-get update
     sudo apt-get install build-essential python-dev python-pip python-smbus git

# Ensure that Raspberry pi GPIO library is installed
To validate the RPI.GPIO library installation, run the following commmand in the raspberry pi terminal
     
     sudo pip install RPi.GPIO

# Library Install
To download the neccesary libraries for the MAX 31855, run the following commands in the rapsberry pi terminal

     cd ~
     git clone https://github.com/adafruit/Adafruit_Python_MAX31855.git
     cd Adafruit_Python_MAX31855
     sudo python setup.py install



# Adafruit Python MCP3008

Python code to use the MCP3008 analog to digital converter with a Raspberry Pi or BeagleBone black.

## Installation

To install the library from source (recommended) run the following commands on a Raspberry Pi or other Debian-based OS system:

    sudo apt-get install git build-essential python-dev
    cd ~
    git clone https://github.com/adafruit/Adafruit_Python_MCP3008.git
    cd Adafruit_Python_MCP3008
    sudo python setup.py install

Alternatively you can install from pip with:

    sudo pip install adafruit-mcp3008

Note that the pip install method **won't** install the example code.
