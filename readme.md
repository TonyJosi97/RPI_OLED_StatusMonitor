## Luma.OLED

### Installation

`sudo -H pip3 install --upgrade luma.oled`

### Permissions

luma.oled uses hardware interfaces that require permission to access. After you have successfully installed luma.oled you may want to add the user account that your luma.oled program will run as to the groups that grant access to these interfaces.:

`sudo usermod -a -G spi,gpio,i2c pi`


### PS Util (Was already there)

`pip3 install psutil`

### OWM - OpenWeatherMaps

`pip3 install pyowm`

