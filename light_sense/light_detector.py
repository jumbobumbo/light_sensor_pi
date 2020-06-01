from common.edge import TimeTillEdge as TTE
from common.validator import key_validator
from requests import post
from json import load
from pathlib import Path
from time import sleep
from functools import wraps
from re import search as r_search

# Path to parent DIR
mod_path = Path(__file__).parent

def retry(resp_code: int = 500, retries: int = 2, delay: int = 5):
    """
    retry decorator

    Keyword Arguments:
        resp_code {int} -- http response code from operation
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
                response = r_search(f"\[(.*)\]", func_call).group(1)
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

class SetLight:

    def __init__(self, conf_file="conf.json"):
        self.config = conf_file

    @property
    def config(self) -> dict:
        # validation
        unwanted_keys = key_validator(["bulbs", "web_uri", "light_attribs", "time_triggers"], self.__config)
        if unwanted_keys:
            raise KeyError(f"unwanted keys: {unwanted_keys}\n"
                           f"expected keys: bulbs, web_uri, light_attribs, time_triggers"
                           )
        # return if good
        return self.__config

    @config.setter
    def config(self, conf_file):
        with open(Path(mod_path, "config", conf_file), "r") as f:
            self.__config = load(f)

    @retry(resp_code=200)
    def poster(self, url: str, json: dict) -> object:
        """
        Arguments:
            url {str} -- url to post to
            json {dict} -- dictionary object sent as json to post URL

        Returns:
            object -- object returned from post
        """
        return post(url, json=json)

    def light_level_reached(self,  bulb_name: str) -> bool:
        """
        returns true if the trigger time is met

        Arguments:
            bulb_name {str} -- name of bulb in conf file

        Returns:
            bool -- True if area is dark enough, False if not
        """
        def _get_gpio_time():
            with TTE() as et:
                return int(et.return_avg_edge_time())

        trigger_time = self.config["time_triggers"][self.config["bulbs"][bulb_name]["group"]]

        if _get_gpio_time() >= trigger_time:
            return True
        else:
            return False

    def light_on(self, bulb_name: str, time_attribs: str):
        """
        turns the bulb on via name (name: ip in conf file)

        Arguments:
            bulb_name {str} -- name of bulb in conf file
            time_attribs {str} -- day or night
        """
        send_data = {
            "ip": self.config["bulbs"][bulb_name]["ip"],
            "actions": ["on"],
            "attribs": {
                "hsb":  self.config["light_attribs"][time_attribs]["hsb"]
            }
        }

        return poster(f"{self.config['web_uri']}/tplbulb_set/", json=send_data)

    def light_off(self, bulb_name: str):
        """
        turns the bulb off via name (name: ip in conf file)

        Arguments:
            bulb_name {str} -- name of bulb in conf file
        """
        send_data = {
            "ip": self.config["bulbs"][bulb_name]["ip"],
            "actions": ["off"]
        }

        return poster(f"{self.config['web_uri']}/tplbulb_set/", json=send_data)

if __name__ == "__main__":
    SetLight().light_on("office", "day")
    #SetLight().light_off("office")
