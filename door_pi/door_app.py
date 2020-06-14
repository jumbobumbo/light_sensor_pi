from common.gpio_events import GPIOEvent
from requests import post
from time import time, sleep
from datetime import datetime
from functools import wraps
from re import search as r_search
from json import JSONDecodeError

# move to config file
on = {"Bedroom": {"power": "on", "color": [750, 1000, 65000, 1000]}}
off = {"Bedroom": {"power": "off"}}
get = {"Bedroom": ["power"]}
days = {
    "Monday": ["09:00:00", "22:00:00"],
    "Tuesday": ["09:00:00", "22:00:00"],
    "Wednesday": ["09:00:00", "22:00:00"],
    "Thursday": ["09:00:00", "22:00:00"],
    "Friday": ["09:00:00", "22:00:00"],
    "Saturday": ["11:00:00", "23:00:00"],
    "Sunday": ["11:00:00", "23:00:00"]
}


def retry(resp_code: str = "500", retries: int = 3, delay: int = 2):
    """
    retry decorator

    Keyword Arguments:
        resp_code {str} -- http response code from operation
        retries {int} -- num of retries (default: {2})
        delay {int} -- time is seconds beween each retry (default: {5})
    """
    def retry_dec(f: object):

        @wraps(f)
        def retry_f(*args, **kwargs):
            retry_num = retries
            while retry_num > 1:
                # attempt to call func
                func_call = f(*args, **kwargs)
                response = r_search(f"\[(.*)\]", str(func_call)).group(1)
                if response == resp_code:  # we didn't want to see that code
                    retry_num -= 1
                    # wait delay before try
                    sleep(delay)
                else:  # response code is acceptable
                    return func_call
            # last chance to connect
            return f(*args, **kwargs)

        return retry_f

    return retry_dec

@retry()
def poster(url: str, json: dict) -> dict:
    return post(url, json=json)

if __name__ == "__main__":
    with GPIOEvent(return_vals={"high": "open", "low": "closed"}) as gpio:
        last_event = [gpio.event_status, int(time())]
        while True:
            sleep(0.2)  # lets not max out the CPU
            day_time = datetime.now().strftime("%A - %H:%M:%S").split(" - ")
            if days[day_time[0]][0] < day_time[1] < days[day_time[0]][1]:  # allow for quiet time
                current_status = gpio.event_status
                print(f"cs: {current_status}, gpstatus: {gpio.event_status}")
                if current_status != last_event[0]:
                    post_data = poster("http://192.168.1.149:8082/lifxbulb_get/", json=get)
                    try:
                        power = post_data.json()
                    except JSONDecodeError:
                        print(post_data)
                        continue
                    tn = int(time())
                    if tn - last_event[1] >= 5:
                        if power["Bedroom"][0] == "off":
                            if last_event[0] == "open" and current_status == "closed":
                                last_event[0] = current_status
                            else:
                                last_event[0], last_event[1] = current_status, tn
                                poster("http://192.168.1.149:8082/lifxbulb_set/",json=on)
                                print("on")
                                print(last_event[0])
                        if power["Bedroom"][0] == "on":
                            if last_event[0] == "closed" and current_status == "open":
                                last_event[0] = current_status
                            else:
                                last_event[0], last_event[1] = current_status, tn
                                poster("http://192.168.1.149:8082/lifxbulb_set/",json=off)
                                print("off")
                                print(last_event[0])
                    else:
                        last_event[0], last_event[1] = current_status, tn
                        print("no change")
                        print(last_event[0])