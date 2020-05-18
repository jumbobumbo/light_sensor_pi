import RPi.GPIO as GPIO
from time import sleep, time


class TimeTillEdge:
    """
    MUST UTILISE 'WITH' TO FUNCTION
    """

    def __init__(self, gpio_mode: str = "board", gpio_pin: int = 7, edge: str = "rising", timeout: int = 45000):
        """
        Waits for edge(s) on a specified gpio pin
        Default gpio mode is BOARD

        Keyword Arguments:
            gpio_mode {str} -- GPIO mode - BOARD/BCM (default: {"board"})
            gpio_pin {int} -- GPIO pin number (default: {7})
            edge {str} -- Rising, falling or both (default: {"rising"})
            timeout {int} -- in MS - max wait time before giving up (default: {45000})
        """
        self.gpio = GPIO
        self.gpio_pin = gpio_pin
        board_dict = {"board": GPIO.BOARD, "bcm": GPIO.BCM}
        self.gpio_mode = board_dict[gpio_mode.lower()]
        edge_dict = {"rising": GPIO.RISING, "falling": GPIO.FALLING, "both": GPIO.BOTH}
        self.edge = edge_dict[edge.lower()]
        self.timeout = timeout

    def __enter__(self):
        self.gpio.setmode(GPIO.BOARD)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.gpio.cleanup()

    def return_avg_edge_time(self): 
        """
        returns a
        """


if __name__ == "__main__":
