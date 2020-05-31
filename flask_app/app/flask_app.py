from flask import Flask, request
from common.connection_manager import TPLConn as TPL
from common.sun_coms import RetrieveSunRiseSet as SunSet

from time import sleep


# flask object
app = Flask(__name__, static_url_path="")

@app.route("/")
def test_flask() -> str:
    """
    simply for test
    :return: str
    """
    return "<h1>Pages:</h1><p>tplbulb_set</p><p>tplbulb_get</p>"

@app.route("/tplbulb_set/", methods=["POST"])
def tpl_bulb_set() -> dict:
    """
    controls TPLlight bulbs
    Expected JSON args: MORE TO COME
    example input:
    {
        "ip": "192.168.1.141",
        "actions" : ["on"],
        "attribs": {
            "hsb": [240, 75, 100]
        }
    }

    Returns:
        dict: returns the bulb properties dict
    """
    post_data = request.get_json()

    # basic verification to check 'ip' key is present
    if key_validator(["ip"], post_data):
        return "An IP must be given to create a bulb connection"

    # connect to bulb
    with TPL(post_data["ip"]) as bulb:
        if "actions" in post_data:
            # complete bulb actions
            for action in post_data["actions"]:
                run = getattr(bulb, action)
                run()
                sleep(0.5)

        if "attribs" in post_data:
            # set bulb attributes
            for key, val in post_data["attribs"].items():
                setattr(bulb, key, val)

        return_data = bulb.__dict__

    return return_data

@app.route("/tplbulb_get/", methods=["POST"])
def tpl_bulb_get() -> dict:
    """
    Allows you to get without setting anything

    Returns:
        dict: returns the bulb properties dict
    """
    post_data = request.get_json()

    # basic verification to check 'ip' key is present
    if key_validator(["ip"], post_data):
        return "An IP must be given to create a bulb connection"

    with TPL(post_data["ip"]) as bulb:
        return bulb.__dict__

@app.route("/sun_get/", methods=["POST"])
def sunrise_api_get() -> dict:
    """
    Retrives the sunrise and sunset information of a given location and day
    Example post input:
        {"lat": 12.34, "lng": 0.089600, "date": "today"}

    Returns:
        dict -- example response:
            {'results': {'sunrise': '2020-05-30T05:33:21+00:00', 'sunset': '2020-05-30T18:21:19+00:00'}}
    """
    post_data = request.get_json()

    # basic verification to check if req keys are present
    invalid_keys = key_validator(["lat", "lng", "date"], post_data)
    if invalid_keys:
        return f"following keys are not valid: {invalid_keys}\n" \
               f"only: lat, lng and date are valid"

    return SunSet().req_data_from_response(post_data)

def key_validator(keys: list, data: dict) -> list:
    """
    Returns a list of keys that aren't present in the data dict
    If all are present, returns nothing

    Arguments:
        keys {list} -- list of keys
        data {dict} -- dict to verify

    Returns:
        list/ None
    """
    return_list = []
    for key in keys:
        if key not in data.keys():
            return_list.append(key)

    if len(return_list) > 0:
        return return_list


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8082)
