import esp32
import network
import machine
import ntptime
import utime

from constants import SSID, PSWD


def get_temp():
    temp_f = esp32.raw_temperature()
    temp_c = (temp_f - 32.0) * 0.56
    return temp_c


def wifi_connect(station_interface: network.WLAN) -> None:
    station_interface.active(True)
    if not station_interface.isconnected():
        station_interface.connect(SSID, PSWD)


def wifi_disconnect(station_interface: network.WLAN) -> None:
    if station_interface.isconnected():
        station_interface.disconnect()
    station_interface.active(False)


class TimeUpdater:

    def __init__(self, time_zone = 2):
        self.time_zone = time_zone
        self.completed = False

    def update(self, rtc: RTC) -> None:
        if not self.completed:
            ntptime.settime()
            time_tuple = utime.localtime(utime.mktime(utime.localtime()) + self.time_zone * 3600)
            time_tuple = time_tuple[0:3] + (0,) + time_tuple[3:6] + (0,)
            rtc.datetime(time_tuple)
            self.completed = True


def transform_bytearray(color_array: bytearray, goal_array: bytearray, number_of_steps = 50) -> None:
    current_step = 0
    difference = tuple(map(lambda x, y: (x - y) / number_of_steps, goal_array, color_array))
    while current_step < number_of_steps:
        current_step += 1
        new_colors = tuple(map(lambda x, y: round(x + y * current_step), color_array, difference))
        yield bytearray(new_colors)


def set_leds_color(leds: NeoPixel, color_array: bytearray) -> None:
    leds.fill(color_array)
    leds.write()


# from neopixel import NeoPixel
# from machine import Pin
# pin23 = Pin(23, Pin.OUT)
# led_strip = NeoPixel(pin23, 1)
# led_strip[0] = (255, 255, 255)
# lead_strip.write()



