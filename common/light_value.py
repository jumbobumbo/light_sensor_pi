import RPi.GPIO as GPIO
from time import sleep


class LightValueList:
    """
    MUST UTILISE 'WITH' TO FUNCTION
    """

    def __init__(self, gpio_pin: int = 7):
        """
        Requires an LDR and capacitor to be wired in to the breadboard
        Guide, and core of code from here:
            https://pimylifeup.com/raspberry-pi-light-sensor/
            Check it out!

        Keyword Arguments:
            gpio_pin {int} -- GPIO pin number (default: {7})
        """
        self.gpio_pin = gpio_pin
        self.gpio = GPIO

    def __enter__(self):
        self.gpio.setmode(GPIO.BOARD)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.gpio.cleanup()

    def return_light_value(self) -> int:
        """
        The higher the count, the darker it is.
        'Normal' values at different light levels will vary from pi to pi

        Returns:
            int -- the number of times it took to go round the while loop
        """
        # set pin to output
        self.gpio.setup(self.gpio_pin, self.gpio.OUT)
        self.gpio.output(self.gpio_pin, self.gpio.LOW)
        # catch up time
        sleep(0.1)

        # set pin to input
        self.gpio.setup(self.gpio_pin, self.gpio.IN)

        # add to count until pin value is high
        count = 0
        while (self.gpio.input(self.gpio_pin) == self.gpio.LOW):
            count += 1

        return count


if __name__ == "__main__":
    with LightValueList() as lightvals:
        for i in range(0, 10):
            print(lightvals.return_light_value())
