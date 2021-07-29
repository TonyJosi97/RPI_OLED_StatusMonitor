# Main file

from luma.core.interface.serial import i2c
from luma.core.interface.parallel import bitbang_6800
from luma.core.render import canvas
from luma.oled.device import sh1106
import subprocess
import datetime
from time import sleep
import psutil
from pyowm import OWM
from pyowm.utils import config
from pyowm.utils import timestamps

AUTH_TOKEN_FILE_PATH = "./owm_api_key.txt"

## Globals
owm_manager = None

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

def get_cpu_util_percent():
    return psutil.cpu_percent()

def get_ram_util_percent():
    return psutil.virtual_memory().percent

def get_date_time():
    date_time_str = str(datetime.datetime.now())
    date_time = ['0', '0']
    try:
        date_time_str = date_time_str.split()
        date_ = date_time_str[0]
        time_ = date_time_str[1]
        time_ = time_.split(".")
        time_ = time_[0]
        date_time[0] = date_
        date_time[1] = time_
    except Exception as _:
        pass

    return date_time

def read_entire_file(f_name):

    try:
        with open(f_name) as file_con:
            data = file_con.read()
        return data
    except Exception as e:
        return -1


def get_owm_authtoken():

    auth_token = read_entire_file(AUTH_TOKEN_FILE_PATH)
    if not auth_token == -1:
        final_authtk = auth_token.strip()
        return final_authtk
    else:
        return -1

def init_modules():
    
    global owm_manager
    owm = OWM(str(get_owm_authtoken()))
    owm_manager = owm.weather_manager()

def get_weather_data():
    global owm_manager
    observation = owm_manager.weather_at_place('Karukachal,IN')
    w = observation.weather
    temptr = w.temperature('celsius')
    return [str(temptr.get("temp")), str(w.clouds), str(w.detailed_status)]

# rev.1 users set port=0
# substitute spi(device=0, port=0) below if using that interface
# substitute bitbang_6800(RS=7, E=8, PINS=[25,24,23,27]) below if using that interface
serial = i2c(port=1, address=0x3C)

# substitute ssd1331(...) or sh1106(...) below if using that device
device = sh1106(serial)

with canvas(device) as draw:
    draw.rectangle(device.bounding_box, outline="white", fill="black")
    draw.text((30, 40), "Hello World", fill="white")


if __name__ == "__main__":

    init_modules()

    print(get_temp())
    print(get_cpu_util_percent())
    print(get_date_time())
    print(get_ram_util_percent())
    print(get_weather_data())
