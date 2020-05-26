from requests import get
from re import search as r_search


class RetrieveSunRiseSet:
    def __init__(self, uri: str = "api.sunrise-sunset.org"):
        self.uri = uri

    def _return_between_markers(self, input_string: str, m_chars: list = ["\[", "\]"]) -> str:
        """
        example with default m_chars: input "<response [200]>", return "200"
        Arguments:
            input_string {str} -- string you wish to search in

        Keyword Arguments:
            m_chars {list} -- character markers (default: {["\[", "\]"]})

        Returns:
            str -- text between markers
        """
        return r_search(f"{m_chars[0]}(.*){m_chars[1]}", input_string).group(1)

    def return_response_json(self, input_data: dict) -> dict:
        """
        returns response sunrie response json as dict

        Arguments:
            input_data {dict} -- example: {"lat": 12.34, "lng": 0.089600, "date": "today"}

        Returns:
            dict -- dict object from api
        """
        unsupported_keys = []

        for key in input_data.keys():
            if key not in ["lat", "lng", "date"]:
                unsupported_keys.append(key)

        if len(unsupported_keys) > 0:
            raise KeyError(
                f"Keys must be: ['lat', 'lng', 'date'], not {unsupported_keys}")

        response = get(
            f"https://{self.uri}/json?lat={input_data['lat']}&lng={input_data['lng']}&date={input_data['date']}&formatted=0")

        res_code = self._return_between_markers(str(response))

        if res_code == "200":
            return response.json()
        else:
            return ValueError(f"unexpected response code: {res_code}")

    def req_data_from_response(self, input_data: dict, dict_keys: list = ["sunrise", "sunset"]) -> dict:
        """
        Arguments:
            input_data {dict} --  example: {"lat": 12.34, "lng": 0.089600, "date": "today"}

        Keyword Arguments:
            dict_keys {list} -- keys you want to retrieve the data for (default: {["sunrise", "sunset"]})

        Returns:
            dict - dict of requested keys, if none specified returns all from 'results'
        """
        json_resp = self.return_response_json(input_data)

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
