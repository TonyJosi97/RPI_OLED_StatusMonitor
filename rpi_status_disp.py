# Main file

from luma.core.interface.serial import i2c
from luma.core.interface.parallel import bitbang_6800
from luma.core.render import canvas
from luma.oled.device import sh1106
import subprocess
import datetime
import time 
import psutil
from pyowm import OWM
from pyowm.utils import config
from pyowm.utils import timestamps
import RPi.GPIO as GPIO

AUTH_TOKEN_FILE_PATH = "./owm_api_key.txt"
WEATHER_CHECK_DELAY_SEC = 3600 # 1 hour delay
WAIT_FOR_INTERNET_RETRY = 60 # Each retry takes approx 1 sec (1 sec sleep used)
CPU_FAN_SIGNAL_GPIO = 17
CPU_FAN_TURN_ON_THRESH = 56
CPU_FAN_TURN_OFF_THRESH = 40

## Oled Display alignment
OLED_LEFT_PADDING = 10

## Globals
g_owm_manager = None
g_oled_disp_sh1106 = None
g_prev_weather_check_time = 0.0
g_weather_data = None
g_got_weather_data = False
g_cur_temp = 0
g_cpu_fan_on = False

def get_temp(window = 20, samp_period_ms = 20):
    temp_sum = 0

    for _ in range(window):
        out = subprocess.run(['vcgencmd', 'measure_temp'], stdout=subprocess.PIPE).stdout.decode('utf-8')
        t_arr = out.split("=")
        t_arr = t_arr[1]
        t_arr =t_arr.split("'")
        temp = float(t_arr[0])
        temp_sum += temp
        time.sleep(samp_period_ms / 1000)

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


def check_network_connection():

    try:
        cmd_resp = subprocess.check_output(['curl', '-Is', 'http://www.google.com'])
        cmd_resp = cmd_resp.decode("utf-8") 
        cmd_resp_list = cmd_resp.split("\r\n")
        header_n1 = cmd_resp_list[0]

        header_n1 = header_n1.strip()
        if header_n1 == "HTTP/1.1 200 OK":
            return 1
        else:
            return 0

    except:
        return -1

def init_modules():

    # Init open weather map API
    global g_owm_manager
    owm = OWM(str(get_owm_authtoken()))
    g_owm_manager = owm.weather_manager()

    # Init GPIO API
    GPIO.setmode(GPIO.BCM)                              # choose BCM GPIO address layout 
    GPIO.setup(CPU_FAN_SIGNAL_GPIO, GPIO.OUT)           # set CPU_FAN_SIGNAL_GPIO as an output 


def init_device():
    global g_oled_disp_sh1106
    # rev.1 users set port=0
    # substitute spi(device=0, port=0) below if using that interface
    # substitute bitbang_6800(RS=7, E=8, PINS=[25,24,23,27]) below if using that interface
    serial = i2c(port=1, address=0x3C)

    # substitute ssd1331(...) or sh1106(...) below if using that device
    g_oled_disp_sh1106 = sh1106(serial)

def get_weather_data():
    global g_owm_manager
    observation = g_owm_manager.weather_at_place('Karukachal,IN')
    w = observation.weather
    temptr = w.temperature('celsius')
    return [str(temptr.get("temp")), str(w.clouds), str(w.detailed_status), str(w.humidity), str(w.rain)]


def limit_str_size(data):
    if len(data) > 4:
        return data[:4]
    else:
        return data

def get_current_cpu_freq():
    data_ = str(float(psutil.cpu_freq().current) / 1000)
    return data_[:3]


def update_oled_screen():

    global g_oled_disp_sh1106, g_prev_weather_check_time, g_weather_data, g_got_weather_data, g_cur_temp

    with canvas(g_oled_disp_sh1106) as draw:
        #draw.rectangle(device.bounding_box, outline="white", fill="black")
        #draw.text((5, 5), "TONY'S RPI 4", fill="white")
        parsed_cpu_util = str(get_cpu_util_percent())
        parsed_cpu_util = limit_str_size(parsed_cpu_util)
        parsed_ram_util = str(get_ram_util_percent())
        parsed_ram_util = limit_str_size(parsed_ram_util)
        draw.text((OLED_LEFT_PADDING, 4), "CPU:" + parsed_cpu_util + "% RAM:" + parsed_ram_util + "%", fill="white")
        g_cur_temp = get_temp()
        parsed_temp = str(g_cur_temp)
        parsed_temp = limit_str_size(parsed_temp)
        draw.text((OLED_LEFT_PADDING, 14), "TMP:" + parsed_temp + " FRQ:" + get_current_cpu_freq() + "G", fill="white")

        draw.text((OLED_LEFT_PADDING, 22), "-------------------", fill="white")

        if time.time() - g_prev_weather_check_time > WEATHER_CHECK_DELAY_SEC or g_got_weather_data == False:

            nw_conn_retry_tmp = 0
            g_weather_data = ["OWM", "ERR", ":(", "_", "_"]
            while nw_conn_retry_tmp < WAIT_FOR_INTERNET_RETRY:
                nw_conn_retry_tmp += 1
                try:
                    init_modules()
                    g_weather_data = get_weather_data()
                    g_got_weather_data = True
                except:
                    time.sleep(1) # retry after 1 sec
                    continue
                break

            g_prev_weather_check_time = time.time() 

        try:
            draw.text((OLED_LEFT_PADDING, 30), "TMP:" + limit_str_size(g_weather_data[0]) + " CLD:" + g_weather_data[1], fill="white")
            draw.text((OLED_LEFT_PADDING, 40), "HMD:" + g_weather_data[3] + " RN:" + g_weather_data[4], fill="white")
            draw.text((OLED_LEFT_PADDING, 50), "STS:" + g_weather_data[2], fill="white")
        except:
            pass

def cpu_fan_control():
    
    global g_cur_temp, g_cpu_fan_on
    try:
        if g_cur_temp >= CPU_FAN_TURN_ON_THRESH and not g_cpu_fan_on:
            GPIO.output(CPU_FAN_SIGNAL_GPIO, True)
            g_cpu_fan_on = True
        elif g_cur_temp <= CPU_FAN_TURN_OFF_THRESH and g_cpu_fan_on:
            GPIO.output(CPU_FAN_SIGNAL_GPIO, False)
            g_cpu_fan_on = False
    except KeyboardInterrupt:
        GPIO.cleanup()

if __name__ == "__main__":

    # Wait for internet to be up and running, (wait for max approx. 60 secs)
    connected_to_nw = False
    nw_conn_retry = 0
    while not connected_to_nw and nw_conn_retry < WAIT_FOR_INTERNET_RETRY:
        if check_network_connection() == 1:
            connected_to_nw = True
            break
        time.sleep(1) # retry after 1 sec
        nw_conn_retry += 1

    try:
        init_modules()
        init_device()
    except Exception as _:
        print(_)

    while True:
        update_oled_screen()
        cpu_fan_control()       ## Control CPU cooling fan based on temperature
        time.sleep(1 - 0.4)     ## Update every 1 sec, CPU temp calc function takes aprox 400 ms
