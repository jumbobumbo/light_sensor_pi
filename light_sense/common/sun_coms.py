from requests import get
from re import search as r_search


class RetrieveSunRiseSet:
    def __init__(self, uri: str = "api.sunrise-sunset.org"):
        self.uri = uri

    def _return_between_markers(self, input_string: str, w_chars: list = ["\[", "\]"]) -> str:
        res = r_search(f"{w_chars[0]}(.*){w_chars[1]}", input_string)
        return res.group(1)

    def return_response_json(self, get_data: dict) -> dict:
        """
        returns response sunrie response json as dict

        Arguments:
            get_data {dict} -- example: {"lat": 12.34, "lng": 0.089600, "date": "today"}

        Returns:
            dict -- dict object from api
        """
        unsupported_keys = []

        for key in get_data.keys():
            if key not in ["lat", "lng", "date"]:
                unsupported_keys.append(key)

        if len(unsupported_keys) > 0:
            raise KeyError(
                f"Keys must be: ['lat', 'lng', 'date'], not {unsupported_keys}")

        response = get(
            f"https://{self.uri}/json?lat={get_data['lat']}&lng={get_data['lng']}&date={get_data['date']}&formatted=0")

        res_code = self._return_between_markers(str(response))

        if res_code == "200":
            return response.json()
        else:
            return ValueError(f"unexpected response code: {res_code}")

    def req_data_from_response(self, get_data: dict, dict_keys: list = ["sunrise", "sunset"]) -> dict:
        """
        [summary]

        Arguments:
            get_data {dict} -- [description]

        Keyword Arguments:
            dict_keys {list} -- [description] (default: {["sunrise", "sunset"]})

        Returns:
            dict - dict of requested keys, if none specified returns all from 'results'
        """
        json_resp = self.return_response_json(get_data)

        if len(dict_keys) == 0:
            # removes the status key, val pair but it keeps everything else
            return json_resp["results"]
        else:
            # returns the specified keys from the result
            response_dict = {"results": {}}

            for key in dict_keys:
                response_dict["results"][key] = json_resp["results"][key]
            return response_dict


if __name__ == "__main__":
    test = RetrieveSunRiseSet()
    print(test.req_data_from_response(
        {"lat": 12.34, "lng": 0.089600, "date": "today"}))
