import esp32
import machine
import utime
import sys
from functions import *
from constants import *
from neopixel import NeoPixel


class Main:

    def __init__(self):
        # color array configuration
        self.color_array = bytearray([0, 0, 0])
        self.color_array_iterator = None
        self.color_update_frequency = 50

        # RTC configuration
        self.rtc = machine.RTC()
        self.time_updater = TimeUpdater(rtc=self.rtc, time_zone=2)
        self.timer_0 = machine.Timer(0)
        self.timer_1 = machine.Timer(1)
        self.timer_2 = machine.Timer(2)
        self.timer_3 = machine.Timer(3)

        # wlan interfaces configuration
        self.wifi = network.WLAN(network.STA_IF)
        wifi_connect(self.wifi)
        self.timer_1.init(period=5000, mode=machine.Timer.ONE_SHOT, callback=self.update_RTC)

        # Pins configuration
        self.repl_pin = machine.Pin(0, machine.Pin.IN, machine.Pin.PULL_UP)
        self.input_pin_1 = machine.Pin(INPUT_PIN_1, machine.Pin.OUT)
        self.input_pin_1.irq(trigger=machine.Pin.IRQ_RISING, handler=self.switch_mode)
        self.input_pin_2 = machine.Pin(INPUT_PIN_2, machine.Pin.OUT)
        self.input_pin_3 = machine.Pin(INPUT_PIN_3, machine.Pin.OUT)

        self.leds_pin = machine.Pin(LED_DATA_PIN, machine.Pin.OUT)
        self.leds = NeoPixel(self.leds_pin, NUMBER_OF_LEDS)

        # Configuration loading
        self.configuration = Configuration()
        self.modes = self.get_modes()
        self.mode_iterator = None
        self.mode_call = time_to_ms(*utime.localtime()[3:6])
        self.mode = None
        self.get_next_mode()
        self.update_color_array()

    def loop(self):
        while True:
            if self.repl_pin.value() == 0:
                print("Dropping to REPL")
                # timer_0.deinit()
                # self.wake_timer.deinit()
                sys.exit()

            elif get_temp() > MAX_TEMPERATURE:
                set_leds_color(leds, (0, 0, 0))
                utime.sleep_ms(500)

            else:
                set_leds_color(self.leds, self.color_array)

    def switch_mode(self, pin):
        current_time = time_to_ms(*utime.localtime()[3:6])
        if current_time - self.mode_call > self.configuration.PIN_TIMEOUT:
            self.mode_call = current_time
            self.get_next_mode()
            self.color_array_iterator = self.mode(self.color_array)
            self.update_color_array()



    def get_next_mode(self):
        try:
            self.mode = next(self.mode_iterator)
        except (TypeError, StopIteration):
            self.mode_iterator = (mode for mode in self.modes)
            self.mode = next(self.mode_iterator)
        print("Switched to mode:", self.mode.__name__)

    def update_RTC(self, _):
        self.timer_1.deinit()
        if self.wifi.isconnected():
            self.time_updater.update()
            self.timer_1.init(period=5000, mode=machine.Timer.ONE_SHOT, callback=self.update_alarms)
        else:
            self.timer_1.init(period=5000, mode=machine.Timer.ONE_SHOT, callback=self.update_RTC)

    def update_alarms(self, _):
        print(get_ms_to_alarm(self.configuration.wake_time, self.configuration.wake_duration))
        # self.timer_2.deinit()
        # self.timer_2.init()
        # self.timer_3.deinit()
        # self.timer_3.init()

    def get_modes(self):
        return [getattr(LampModes, mode) for mode in self.configuration.modes]

    def update_color_array(self, _=None):
        # _=None required to be callable by timer
        try:
            self.color_array = next(self.color_array_iterator)
            self.timer_0.init(period=self.color_update_frequency, mode=machine.Timer.ONE_SHOT, callback=self.update_color_array)
        except StopIteration:
            self.timer_0.deinit()

    def



main = Main()
main.loop()