import esp32
import machine
import utime
import sys
from functions import *
from constants import *
from neopixel import NeoPixel

# Pins configuration
repl_pin = machine.Pin(0, machine.Pin.IN, machine.Pin.PULL_UP)
leds_pin = machine.Pin(LED_DATA_PIN, machine.Pin.OUT)
input_pin_1 = machine.Pin(INPUT_PIN_1, machine.Pin.OUT)
input_pin_2 = machine.Pin(INPUT_PIN_2, machine.Pin.OUT)
input_pin_3 = machine.Pin(INPUT_PIN_3, machine.Pin.OUT)

# leds configuration
leds = NeoPixel(leds_pin, NUMBER_OF_LEDS)

# wlan interfaces configuration
wifi = network.WLAN(network.STA_IF)
wifi_connect(wifi)
# access_point = network.WLAN(netowk.AP_IF)

# RTC config
rtc = machine.RTC()
time_updater = TimeUpdater(time_zone=2)

while True:

    if repl_pin.value() == 0:
        print("Dropping to REPL")
        sys.exit()

    elif get_temp() > MAX_TEMPERATURE:
        set_leds_color(leds, (0, 0, 0))
        utime.sleep(10)

    else:
        if wifi.isconnected():
            time_updater.update(rtc)
        set_leds_color(leds, (0, 64, 0))
        utime.sleep(1)
        set_leds_color(leds, (0, 0, 0))
        utime.sleep(1)

