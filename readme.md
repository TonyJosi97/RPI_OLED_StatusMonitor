## RPI_OLED_StatusMonitor

RPI_OLED_StatusMonitor is a python script to update the [OLED Display Module - SH1106](https://robu.in/product/0-96-inch-i2c-iic-oled-lcd-module-4pin-with-vcc-gnd-white/) with Raspberry Pi 4 system status such as CPU & RAM utilisation, CPU Frequency, CPU Temperature and also the current weather. The OLED Display Module is connected to the I2C interface of the Raspberry Pi and uses Luma.OLED driver for the communication. 

### System status information sources:
1. CPU & RAM utilisation, CPU Frequency - [psutil](https://pypi.org/project/psutil/)
2. CPU Temperature - Internal [vcgencmd](https://www.raspberrypi.org/documentation/raspbian/applications/vcgencmd.md) tool
3. Weather - [pyowm](https://pypi.org/project/pyowm/) (Requires a valid API key to allow responses from [Openweathermap](https://openweathermap.org/) and the key should be placed in `./owm_api_key.txt` file)

## External Libraries used

### Luma.OLED

#### Installation

`sudo -H pip3 install --upgrade luma.oled`

#### Permissions

luma.oled uses hardware interfaces that require permission to access. After you have successfully installed luma.oled you may want to add the user account that your luma.oled program will run as to the groups that grant access to these interfaces.:

`sudo usermod -a -G spi,gpio,i2c pi`

### psutil

`pip3 install psutil`

### OWM - OpenWeatherMaps

`pip3 install pyowm`

