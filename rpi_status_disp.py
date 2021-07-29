# Main file

from luma.core.interface.serial import i2c
from luma.core.interface.parallel import bitbang_6800
from luma.core.render import canvas
from luma.oled.device import sh1106
import subprocess
import datetime
from time import sleep

def get_temp(window = 20, samp_period_ms = 20):
    temp_sum = 0

    for _ in range(window):
        out = subprocess.run(['vcgencmd', 'measure_temp'], stdout=subprocess.PIPE).stdout.decode('utf-8')
        t_arr = out.split("=")
        t_arr = t_arr[1]
        t_arr =t_arr.split("'")
        temp = float(t_arr[0])
        temp_sum += temp
        sleep(samp_period_ms / 1000)

    return temp_sum / window


# rev.1 users set port=0
# substitute spi(device=0, port=0) below if using that interface
# substitute bitbang_6800(RS=7, E=8, PINS=[25,24,23,27]) below if using that interface
serial = i2c(port=1, address=0x3C)

# substitute ssd1331(...) or sh1106(...) below if using that device
device = sh1106(serial)

with canvas(device) as draw:
    draw.rectangle(device.bounding_box, outline="white", fill="black")
    draw.text((30, 40), "Hello World", fill="white")


