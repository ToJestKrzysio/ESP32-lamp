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
        # self.color_array_iterator = None
        self.color_array_iterator = transform_bytearray(self.color_array, bytearray([255, 128, 64]), number_of_steps=10)

        # Pins configuration
        self.repl_pin = machine.Pin(0, machine.Pin.IN, machine.Pin.PULL_UP)
        self.leds_pin = machine.Pin(LED_DATA_PIN, machine.Pin.OUT)
        self.input_pin_1 = machine.Pin(INPUT_PIN_1, machine.Pin.OUT)
        self.input_pin_1.irq(trigger=machine.Pin.IRQ_RISING, handler=self.switch_mode)
        self.input_pin_2 = machine.Pin(INPUT_PIN_2, machine.Pin.OUT)
        self.input_pin_3 = machine.Pin(INPUT_PIN_3, machine.Pin.OUT)

        self.leds = NeoPixel(self.leds_pin, NUMBER_OF_LEDS)

        # wlan interfaces configuration
        self.wifi = network.WLAN(network.STA_IF)
        wifi_connect(self.wifi)
        # access_point = network.WLAN(netowk.AP_IF)

        # RTC config
        self.rtc = machine.RTC()
        self.time_updater = TimeUpdater(rtc=self.rtc, time_zone=2)
        # self.alarm_time = datetime
        # self.alarm = machine.RTC.alarm()

        # Configuration loading
        self.config = Configuration()
        self.modes = self.config.modes
        self.mode_iterator = None
        self.get_next_mode()
        self.mode_call = None

        # Timers Configuration
        # Rapid timer with frequency of 250ms
        # timer_0 = machine.Timer(0)
        # timer_0.init(mode=machine.Timer.PERIODIC, period=1800, callback= lambda t: print("Called timer 0"))

        # Slower timer with frequency of 20s
        # self.wake_timer = machine.Timer(1)
        # self.wake_timer.init(mode=machine.Timer.PERIODIC, period=5000, callback=self.modify_color_array())

        # color_array_iterator = transform_bytearray(color_array, bytearray([255, 128, 64]), number_of_steps=5)

    # def modify_color_array(self):
    #     print(self.color_array, "MODIFIER")
    #     try:
    #         self.color_array = next(self.color_array_iterator)
    #     except StopIteration or TypeError:
    #         pass

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
                if self.wifi.isconnected():
                    self.time_updater.update()
                get_time_untill_alarm(None, None)
                set_leds_color(self.leds, bytearray([64, 0, 0]))

    def switch_mode(self, pin):
        current_time = utime.localtime()
        try:
            if current_time - self.mode_call > self.config.PIN_TIMEOUT:
                self.mode_call = current_time
                self.get_next_mode()
        except TypeError:
            self.mode_call = current_time
            self.get_next_mode()


    def get_next_mode(self):
        try:
            self.mode = next(self.mode_iterator)
            print(self.mode)
        except (TypeError, StopIteration):
            self.mode_iterator = (mode for mode in self.modes)
            self.mode = next(self.mode_iterator)
            print(self.mode)

main = Main()
main.loop()