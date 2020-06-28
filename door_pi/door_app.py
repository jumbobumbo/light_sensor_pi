from globals.post import poster
from common.gpio_events import GPIOEvent
from time import time, sleep
from datetime import datetime
from json import JSONDecodeError
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# CONFIG - move to config file?
url = "http://192.168.1.210:8082"
bulb_name = "Bedroom"
ignore_time = 5  # time limit of door events to ignore (s)
on = {bulb_name: {"power": "on", "color": [750, 1000, 65000, 1000]}}
off = {bulb_name: {"power": "off"}}
get = {bulb_name: ["power"]}
days = {
    "Monday": ["09:00:00", "22:00:00"],
    "Tuesday": ["09:00:00", "22:00:00"],
    "Wednesday": ["09:00:00", "22:00:00"],
    "Thursday": ["09:00:00", "22:00:00"],
    "Friday": ["09:00:00", "22:00:00"],
    "Saturday": ["11:00:00", "23:00:00"],
    "Sunday": ["11:00:00", "23:00:00"]
}
return_vals = {"high": "open", "low": "closed"}


def post_verify_key(date_time: list,
                    attempts: int = 3,
                    delay: int = 2,
                    url: str = url,
                    json_data: dict = get,
                    bulb_name: str = bulb_name):
    """ Verifies key 'attempts' no of times"""
    attempt = 0

    while attempt < attempts:
        resp = poster(f"{url}/lifxbulb_get/", json=json_data)
        try:
            post_json = resp.json()

            if bulb_name in post_json.keys():
                return post_json

            else:
                print(f"Bulb returned @ {day_time}\n{post_json}")

        except JSONDecodeError:
            print(f"ERROR DECODING BULB RESPONSE:\nTime: {day_time}")

        attempt += 1
        sleep(delay)

    return KeyError(f"Max attempts reached, bulb not returning dict with key: {bulb_name}\n"
                    f"Returned data @ {date_time}: {resp}")


if __name__ == "__main__":
    with GPIOEvent(return_vals=return_vals) as gpio:
        last_event = [gpio.event_status, int(time())]
        while True:
            sleep(0.2)  # lets not max out the CPU
            day_time = datetime.now().strftime("%A - %H:%M:%S").split(" - ")
            if days[day_time[0]][0] < day_time[1] < days[day_time[0]][1]:  # allow for quiet time
                current_status = gpio.event_status
                if current_status != last_event[0]:
                    power = post_verify_key(day_time)
                    tn = int(time())
                    if tn - last_event[1] >= ignore_time:
                        try:
                            if power[bulb_name][0] == "off":
                                if last_event[0] == return_vals["high"] and current_status == return_vals["low"]:
                                    last_event[0] = current_status
                                else:
                                    last_event[0], last_event[1] = current_status, tn
                                    poster(f"{url}/lifxbulb_set/", json=on)
                            if power[bulb_name][0] == "on":
                                if last_event[0] == return_vals["low"] and current_status == return_vals["high"]:
                                    last_event[0] = current_status
                                else:
                                    last_event[0], last_event[1] = current_status, tn
                                    poster(f"{url}/lifxbulb_set/", json=off)
                        except Exception as ex:
                            print(f"exception @: {day_time}\n{ex}")
                    else:
                        last_event[0], last_event[1] = current_status, tn
