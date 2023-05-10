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
PUMP_START_AT_HOUR = 9
PUMP_START_INTERVAL_DAYS = 1
PUMP_OPENED_DURATION_SECONDS = 10


def connect_to_wlan():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid, password)
    while wlan.isconnected() == False:
        sleep(1)

def disconnect_from_wlan():
    wlan = network.WLAN(network.STA_IF)
    wlan.disconnect()
    wlan.active(False)


def get_time_to_sleep(current_timestamp):
    # sleep till next day at PUMP_START_AT_HOUR
    target_timestamp = current_timestamp + 1 * DAY
    target_timestamp = (target_timestamp // DAY) * DAY + PUMP_START_AT_HOUR * HOUR
    return target_timestamp - current_timestamp 


def open_pump():
    PUMP_PIN.value(1)
    sleep(PUMP_OPENED_DURATION_SECONDS)
    PUMP_PIN.value(0)


def is_watering_day(timestamp):
    return (get_day_of_year(timestamp) % PUMP_START_INTERVAL_DAYS) == 0


def is_before_watering_time(timestamp):
    return get_hour(timestamp) < PUMP_START_AT_HOUR


def is_watering_time(timestamp):
    return get_hour(timestamp) == PUMP_START_AT_HOUR


def get_hour(timestamp):
    time_tuple = time.localtime(timestamp)
    return time_tuple[3]


def get_day_of_year(timestamp):
    time_tuple = time.localtime(timestamp)
    year_day = time_tuple[7]
    return year_day


def set_rtc_clock():
    try:
        LED_PIN.value(1)
        connect_to_wlan()
        ntptime.settime()	
        disconnect_from_wlan()
        LED_PIN.value(0)
    except KeyboardInterrupt:
        machine.reset()


set_rtc_clock()
while True:
    current_timestamp = time.time() + UTC_OFFSET * HOUR
    if is_watering_time(current_timestamp) and is_watering_day(current_timestamp):
        open_pump()

    time_to_sleep = get_time_to_sleep(current_timestamp)
    print(time_to_sleep)
    sleep(time_to_sleep)
