import esp32
import network
import machine
import ntptime
import utime


def get_temp():
    temp_f = esp32.raw_temperature()
    temp_c = (temp_f - 32.0) * 0.56
    return temp_c


def wifi_connect(station_interface: network.WLAN):
    station_interface.active(True)
    station_interface.connect("Burdel Laguna", "6G9dry5K3")


def wifi_disconnect(station_interface: network.WLAN):
    station_interface.disconnect()
    station_interface.active(False)


def set_time(time_zone = 2):
    ntptime.settime()
    time_tuple = utime.localtime(utime.mktime(utime.localtime()) + time_zone * 3600)
    time_tuple = time_tuple[0:3] + (0,) + time_tuple[3:6] + (0,)
    rtc.datetime(time_tuple)


# from neopixel import NeoPixel
# from machine import Pin
# pin23 = Pin(23, Pin.OUT)
# led_strip = NeoPixel(pin23, 1)
# led_strip[0] = (255, 255, 255)
# lead_strip.write()



