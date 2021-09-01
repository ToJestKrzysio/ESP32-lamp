import esp32
import network
import machine
import ntptime
import utime
import json

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

    def __init__(self, rtc: RTC, time_zone = 2):
        self.time_zone = time_zone
        self.completed = False
        self.rtc = rtc

    def update(self) -> None:
        if not self.completed:
            ntptime.settime()
            time_tuple = utime.localtime(utime.mktime(utime.localtime()) + self.time_zone * 3600)
            time_tuple = time_tuple[0:3] + (0,) + time_tuple[3:6] + (0,)
            self.rtc.datetime(time_tuple)
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


class Configuration:

    def __init__(self):
        self._filename = "config.json"
        self.attribute_list = []
        self.load()

    def load(self):
        """
        Loads configuration from config.json file.
        """
        with open(self._filename, "r") as file_:
            config_dict = json.load(file_)

        self.attribute_list = []
        for key, value in config_dict.items():
            setattr(self, key, value)
            self.attribute_list.append(key)

    def save(self):
        """
        Saves configuration to a config.json file.
        """
        config_dict = {}
        for key in self.attribute_list:
            config_dict[key] = getattr(self, key)

        with open(self._filename, "w") as file_:
            json.dump(config_dict, file_)

    def add(self, key, value):
        """
        Adds attribute <key> equal to <value> to <self>.
        """
        self.attribute_list.append(key)
        setattr(self, key, value)
        self.save()

    def remove(self, key):
        """
        Removes <self>.<key> from configuration file.
        """
        try:
            self.attribute_list.remove(key)
            delattr(self, key)
            self.save()
        except ValueError:
            pass

    def change(self, key: str, value) -> None:
        """
        Changes value of attribute <self>.<key> to <value>.
        """
        if key not in self.attribute_list:
            self.attribute_list.append(key)
        setattr(self, key, value)
        self.save()

    def __str__(self):
        return self.attribute_list


def get_time_untill_alarm(wake_time=None, wake_period=None):
    current_time = utime.localtime()
    current_hour, current_minute, current_second = current_time[3:5]
    wake_time["hour"], wake_time["minute"]


# timer = machine.Timer(0)
# timer.init(10000)
# timer.deinit()

