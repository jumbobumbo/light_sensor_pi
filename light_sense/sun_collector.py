from requests import post
from pathlib import Path
from json import load, dump, JSONDecodeError
from datetime import datetime
from common.validator import key_validator

# Path to parent DIR
mod_path = Path(__file__).parent


class DayLightHours:

    def __init__(self, conf_file="conf.json"):
        """
        Keyword Arguments:
            conf_file {json} -- [json file, must be within "config" DIR] (default: {"config.json"})
        """
        self.config = conf_file

    @property
    def config(self) -> dict:
        # validation
        unwanted_keys = key_validator(["daylight_data", "web_uri"], self.__config)
        if unwanted_keys:
            raise KeyError(f"unwanted keys: {unwanted_keys}\n"
                           f"expected keys: 'daylight_data', 'web_uri'"
                           )
        # return if good
        return self.__config

    @config.setter
    def config(self, conf_file):
        with open(Path(mod_path, "config", conf_file), "r") as f:
            self.__config = load(f)

    def _get_daylight(self) -> dict:
        """
        Sends post requrest to self.config["web_uri"] and returns its json response
        Returns:
            dict -- response json from request
        """
        try:
            response = post(f"{self.config['web_uri']}/sun_get/",
                            json=self.config["daylight_data"])
            response_data = response.json()
        except JSONDecodeError as ex:
            return f"Error parsing json, post response text: {response.text}"

        return response_data

    def write_daylight_data_to_file(self):
        """
        writes returned response from _get_daylight to file
        """
        daylight_data = self._get_daylight()
        write_file = f"error_{datetime.now().strftime('%d_%m_%Y')}.json" if type(
            daylight_data) == str else "daytime_data.json"

        # write to file
        with open(Path(mod_path, "data", write_file), "w") as f:
            dump(daylight_data, f)

if __name__ == "__main__":
    DayLightHours().write_daylight_data_to_file()
