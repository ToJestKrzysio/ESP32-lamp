import esp32
import network
import machine
import ntptime
import utime
import json
import uasyncio

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


def transform_bytearray(color_array: bytearray, goal_array: bytearray, number_of_steps = 50) -> bytearray:
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
        Loads configuration from configuration.json file.
        """
        with open(self._filename, "r") as file_:
            config_dict = json.load(file_)

        self.attribute_list = []
        for key, value in config_dict.items():
            setattr(self, key, value)
            self.attribute_list.append(key)

    def save(self):
        """
        Saves configuration to a configuration.json file.
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

    # TODO list all atributes properly
    def __str__(self):
        return self.attribute_list


def time_to_ms(hours=0, minutes=0, seconds=0, ms=0):
    return hours * 3_600_000 + minutes * 60_000 + seconds * 1_000 + ms

def get_ms_to_alarm(alarm_time: dict, trigger_period=30) -> int:
    current_time = time_to_ms(utime.localtime()[3:6])
    wake_time = time_to_ms(alarm_time["hour"], alarm_time["minute"])
    ms_to_alram = wake_time - current_time
    return ms_to_alram if ms_to_alram >= 0 else 86400000 + ms_to_alram


class LampModes:

    @staticmethod
    def wake_up(self, color_array):
        iterators = [
            transform_bytearray(color_array=color_array, goal_array=bytearray([64, 32, 32]), number_of_steps=100),
            transform_bytearray(color_array=color_array, goal_array=bytearray([128, 128, 128]), number_of_steps=100),
        ]
        final_list = []
        [final_list.extend(list(iterator)) for iterator in iterators]
        return (step for step in final_list)

    @staticmethod
    def red(color_array):
        return transform_bytearray(color_array=color_array, goal_array=bytearray([64, 0, 0]), number_of_steps=50)

    @staticmethod
    def green(color_array):
        return transform_bytearray(color_array=color_array, goal_array=bytearray([0, 64, 0]), number_of_steps=50)

    @staticmethod
    def blue(color_array):
        return transform_bytearray(color_array=color_array, goal_array=bytearray([0, 0, 64]), number_of_steps=50)

    @staticmethod
    def white(color_array):
        return transform_bytearray(color_array=color_array, goal_array=bytearray([64, 64, 64]), number_of_steps=50)


