from flask import Flask, request
from common.connection_manager import TPLConn as TPL
from time import sleep


# flask object
app = Flask(__name__, static_url_path="")

@app.route("/")
def test_flask() -> str:
    """
    simply for test
    :return: str
    """
    return "<h1>Pages:</h1><p>tplbulb_set</p>"

@app.route("/tplbulb_set/", methods=["POST"])
def tpl_bulb_set() -> str:
    """
    controls TPLlight bulbs
    Expected JSON args: MORE TO COME
    example input:
    {
        "ip": "192.168.1.141",
        "actions" : ["on"],
        "attribs": {
            "hsb": (240, 75, 100),
        }
    }

    Returns:
        str -- meaningless string
    """
    post_data = request.get_json()

    # basic verification to check 'ip' key is present
    if "ip" not in post_data:
        raise KeyError("An IP must be given to create a bulb connection")

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

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8082)
