# Getting Started With The Raspberry Pi
First install the SD card with Raspbian pre-installed and follow prompts to install onto the raspberry pi. Credentials are below

     username: pi
     password: raspberry

# Enable I2C and SSH
Click the pi logo, then preferences, then configurations, On the Interfaces tab, set I2C and SSH to Enable and then click OK


Download Putty onto Windows from https://www.putty.org computer to access raspberry pi "headless" (with no monitor connected to raspberry pi)

# Install Node.js on the pi

     curl -sL http://deb.nodesource.com/setup_4.x | sudo -E bash
     sudo apt-get -y install nodejs


# Installing Git
To install the Git, run the following commands in the raspberry pi terminal

     sudo apt install git-all


# Download files from the Gast_Iot_Sensor_Development Git Repository

     git clone https://github.com/wadooddaoud/Gast_Iot_Sensor_Development.git
     cd Gast_Iot_Sensor_Development
     sudo npm install

# Compile the C libraries to use the Azure IoT SDKs for Python
To compile these libraries, run the following commands in the raspberry pi terminal (This may take up to 10 minutes)

     sudo chmod u+x setup.sh
     sudo ./setup.sh


# Ensure that Raspberry pi GPIO library is installed
To validate the RPI.GPIO library installation, run the following commmand in the raspberry pi terminal
     
     sudo pip install RPi.GPIO


# Installing Dependencies and Libraries for MAX 31855 Thermocouple Amplifier
To install the dependencies and libraries, run the following commands in the raspberry pi terminal

     sudo apt-get update
     sudo apt-get upgrade
     cd ~
     cd Gast_Iot_Sensor_Development
     cd Adafruit_Python_MAX31855
     sudo python setup.py install

# Installing Dependencies and Libraries for Adafruit MCP3008 Anolog to Digital Converter
To install the dependencies and libraries from source (recommended), run the following commands in the raspberry pi terminal

    cd ~
    cd Gast_Iot_Sensor_Development
    cd Adafruit_Python_MCP3008
    sudo python setup.py install

# Installing Dependencies and Libraries for Adafruit AM2302 Temp and Humidity Sensor
To install the dependencies and libraries from source (recommended), run the following commands in the raspberry pi terminal

    cd ~
    cd Gast_Iot_Sensor_Development
    cd Adafruit_Python_DHT
    sudo python setup.py install

# Installing Dependencies and Libraries for the Hologram Nova Cellular Modem

     curl -L hologram.io/python-install | bash
     curl -L hologram.io/python-update | bash
     
     

# Running the application on the Raspberry Pi for the endurance unit

     sudo python EnduranceApp.py
  

# Running the application on the Raspberry Pi for the element 7

     sudo python NitroApp.py
