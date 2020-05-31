from common.edge import TimeTillEdge as TTE
from common.validator import key_validator
from requests import post
from json import load
from pathlib import Path

# Path to parent DIR
mod_path = Path(__file__).parent


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

    def light_on(self, bulb_name: str, time_attribs: str):
        """
        [summary]

        Arguments:
            bulb_name {str} -- [description]
            time_attribs {str} -- [description]
        """

        def _get_gpio_time():
            with TTE() as et:
                return int(et.return_avg_edge_time())

        trigger_time = self.config["time_triggers"][self.config["bulbs"][bulb_name]["group"]]

        if trigger_time <= _get_gpio_time():
            send_data = {
                "ip": self.config["bulbs"][bulb_name]["ip"],
                "actions": ["on"],
                "attribs": {
                    "hsb":  self.config["light_attribs"][time_attribs]["hsb"],
                    "temperature": self.config["light_attribs"][time_attribs]["temperature"]
                }
            }

            post(f"{self.config['web_uri']}/tplbulb_set/", json=send_data)

    def light_off(self, bulb_name: str):
        """
        [summary]

        Arguments:
            bulb_name {str} -- [description]
        """
        send_data = {
            "ip": self.config["bulbs"][bulb_name]["ip"],
            "actions": ["off"]
        }

        post(f"{self.config['web_uri']}/tplbulb_set/", json=send_data)


if __name__ == "__main__":
    SetLight().light_on("office", "day")
