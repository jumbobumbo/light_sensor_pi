import RPi.GPIO as GPIO
from time import sleep


class LightValueList:
    def __init__(self, gpio_pin: int = 7, no_vals: int = 100):
        self.gpio_pin = gpio_pin
        self.no_vals = no_vals
        self.gpio = GPIO

    def __enter__(self):
        self.gpio.setmode(GPIO.BOARD)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.gpio.cleanup()

    def return_light_value(self):
        count = 0
        # set pin to output
        self.gpio.setup(self.gpio_pin, self.gpio.OUT)
        self.gpio.output(self.gpio_pin, self.gpio.LOW)
        # catch up time
        sleep(0.1)

        # set pin to input
        self.gpio.setup(self.gpio_pin, self.gpio.IN)

        # add to count until pin value is high
        while (self.gpio.input(self.gpio_pin) == self.gpio.LOW):
            count += 1

        return count

if __name__ == "__main__":
    with LightValueList() as lightvals:
        for i in range(0, 10):
            print(lightvals.return_light_value())
            sleep(0.1)