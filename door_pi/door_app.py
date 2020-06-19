from common.gpio_events import GPIOEvent
from time import time, sleep
from datetime import datetime
from json import JSONDecodeError
import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from globals.post import poster

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
return_vals={"high": "open", "low": "closed"}

if __name__ == "__main__":
    with GPIOEvent(return_vals=return_vals) as gpio:
        last_event = [gpio.event_status, int(time())]
        while True:
            sleep(0.2)  # lets not max out the CPU
            day_time = datetime.now().strftime("%A - %H:%M:%S").split(" - ")
            if days[day_time[0]][0] < day_time[1] < days[day_time[0]][1]:  # allow for quiet time
                current_status = gpio.event_status
                if current_status != last_event[0]:
                    post_data = poster(f"{url}/lifxbulb_get/", json=get)
                    try:
                        power = post_data.json()
                    except JSONDecodeError:  # we've got back nonsense - back to the top
                        print(f"ERROR DECODING BULB RESPONSE:\nTime: {day_time}\nError: {post_data}")
                        continue
                    tn = int(time())
                    if tn - last_event[1] >= ignore_time:
                        if power[bulb_name][0] == "off":
                            if last_event[0] == return_vals["high"] and current_status == return_vals["low"]:
                                last_event[0] = current_status
                            else:
                                last_event[0], last_event[1] = current_status, tn
                                poster(f"{url}/lifxbulb_set/",json=on)
                        if power[bulb_name][0] == "on":
                            if last_event[0] == return_vals["low"] and current_status == return_vals["high"]:
                                last_event[0] = current_status
                            else:
                                last_event[0], last_event[1] = current_status, tn
                                poster(f"{url}/lifxbulb_set/",json=off)
                    else:
                        last_event[0], last_event[1] = current_status, tn
