import RPi.GPIO as GPIO
from time import sleep


class GPIOEvent:

    def __init__(self, pin: int = 7, gpio_mode: str = "board", gpio_event: str = "rising", io: str = "in", pull_up_down: str = "up", bounce: int = 80, return_vals = dict):
        """
        Detects an event of a specified gpio pin

        Args:
            pin (int, optional): GPIO pin num. Defaults to 7.
            gpio_mode (str, optional): "board" or "bcm" - check raspi RPi.GPIO guide for more. Defaults to "board".
            gpio_event (str, optional): what edge are you waitin for: falling, rising, both?. Defaults to "rising".
            io (str, optional): in or out (input, output). Defaults to "in".
            pull_up_down (str, optional): pull the default value of the pin up or down. Defaults to "up".
            bounce (int, optional): debounce value. Defaults to 80.
            return_vals ([type], optional): Requires the keys high and low. Contains the values you wish self.event_status to be populated with. Defaults to dict.
        """
        self.pin = pin
        self.gpio_event = getattr(GPIO, gpio_event.upper())
        self.io = getattr(GPIO, io.upper())
        self.pull_up_down = getattr(GPIO, f"PUD_{pull_up_down.upper()}")
        self.bounce = bounce
        self.return_vals = return_vals
        GPIO.setmode(getattr(GPIO, gpio_mode.upper()))

    def __enter__(self):
        GPIO.setup(self.pin, self.io, pull_up_down=self.pull_up_down)
        GPIO.add_event_detect(self.pin, self.gpio_event, callback=self.event, bouncetime=self.bounce)
        self.event(self.pin)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        GPIO.cleanup()

    def event(self, channel):
        self.event_status = self.return_vals["high"] if GPIO.input(self.pin) else self.return_vals["low"]

if __name__ == "__main__":
    with GPIOEvent(return_vals={"high": "open", "low": "closed"}) as gpio:
        for i in range(0, 3):
            sleep(2)
            print(gpio.event_status)
