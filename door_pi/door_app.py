from common.gpio_events import GPIOEvent
from requests import post
from time import time, sleep
from functools import wraps
from re import search as r_search

# move to config file
on = {"Bedroom": {"power": "on", "color": [750, 1000, 65000, 1000]}}
off = {"Bedroom": {"power": "off"}}
get = {"Bedroom": ["power"]}


def retry(resp_code: str = "500", retries: int = 3, delay: int = 5):
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
def poster(url: str, json: dict) -> object:
    return post(url, json=json)

with GPIOEvent(return_vals={"high": "open", "low": "closed"}) as gpio:
    last_event = [gpio.event_status, int(time())]
    while True:
        # if gpio.event_status == "closed" and last_event[0] != "closed" and int(time()) - last_event[1] > 5:
        #     post("http://192.168.1.149:8082/lifxbulb_set/",json=off)
        #     print("off")
        #     last_event[0], last_event[1] = gpio.event_status, int(time())
        # elif gpio.event_status == "open" and last_event[0] != "open" and int(time()) - last_event[1] > 5:
        #     post("http://192.168.1.149:8082/lifxbulb_set/",json=on)
        #     print("on")
        #     last_event[0], last_event[1] = gpio.event_status, int(time())
        if gpio.event_status != last_event[0]:
            bulb_status = poster("http://192.168.1.149:8082/lifxbulb_get/", json=get)
            power = bulb_status.json()
            if int(time()) - last_event[1] > 5:
                if power["Bedroom"][0] == "off" and gpio.event_status == "open":
                    poster("http://192.168.1.149:8082/lifxbulb_set/",json=on)
                    print("on")
                elif power["Bedroom"][0] == "on" and gpio.event_status == "closed":
                    poster("http://192.168.1.149:8082/lifxbulb_set/",json=off)
                    print("off")
                last_event[0], last_event[1] = gpio.event_status, int(time())