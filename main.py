import network
from time import sleep
import time
import machine
import ntptime

from credentials import password, ssid

PUMP_PIN = machine.Pin(16, machine.Pin.OUT)
LED_PIN = machine.Pin("LED", machine.Pin.OUT)

MINUTE = 60
HOUR = 60 * MINUTE
DAY = 24 * HOUR
UTC_OFFSET = 3
WATERING_TIME = 12


def connect_to_wlan():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid, password)
    while wlan.isconnected() == False:
        print('Waiting for connection...')
        sleep(1)
    ip = wlan.ifconfig()[0]
    print(f'Connected on {ip}')


def disconnect_from_wlan():
    wlan = network.WLAN(network.STA_IF)
    wlan.disconnect()
    wlan.active(False)


def get_time_to_sleep(current_timestamp):
    DAYS_TO_ADD = 0
    if is_even_year_day(current_timestamp) and is_before_watering_time(current_timestamp):
        DAYS_TO_ADD = 0
    elif is_even_year_day(current_timestamp):
        DAYS_TO_ADD = 2
    else:
        DAYS_TO_ADD = 1

    target_timestamp = current_timestamp + DAYS_TO_ADD * DAY
    target_timestamp = (target_timestamp // DAY) * DAY + WATERING_TIME * HOUR
    return target_timestamp - current_timestamp 


def open_pump():
    PUMP_PIN.value(1)
    sleep(10)
    PUMP_PIN.value(0)


def is_even_year_day(timestamp):
    time_tuple = time.localtime(timestamp)
    year_day = time_tuple[7]
    return (year_day % 2) == 0


def is_before_watering_time(timestamp):
    time_tuple = time.localtime(timestamp)
    hour = time_tuple[3]
    return hour < WATERING_TIME


def is_watering_time(timestamp):
    time_tuple = time.localtime(timestamp)
    hour = time_tuple[3]
    return hour == WATERING_TIME

def set_rtc_clock():
    try:
        LED_PIN.value(1)
        connect_to_wlan()
        ntptime.settime()	
        print(f"Time is: ${time.localtime(time.time() + UTC_OFFSET * HOUR)}")
        disconnect_from_wlan()
        LED_PIN.value(0)
    except KeyboardInterrupt:
        machine.reset()

set_rtc_clock()

while True:
    current_timestamp = time.time() + UTC_OFFSET * HOUR
    if is_watering_time(current_timestamp):
        open_pump()

    time_to_sleep = get_time_to_sleep(current_timestamp)
    print(f"Sleeping: {time_to_sleep}")
    sleep(time_to_sleep)
