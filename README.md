# light_sensor_pi  
LDR light sensor, Reed switches - flask - TPLink\Lifx smart bulb control  
  
## Utilises Sunrise-Sunset api for day/night information  
https://sunrise-sunset.org/api  
 
## Utilses lifxlan pip package by Meghan Clark
https://pypi.org/project/lifxlan/

## Utilses the 'tp-link-LB130-Smart-Wi-Fi-Bulb' project by Brian Dorey  
https://github.com/briandorey/tp-link-LB130-Smart-Wi-Fi-Bulb  
### The following python files originate from the project  
- flask_app/common/decrypt.py  
- flask_app/common/tplight.py  
  
### two modifications made locally by me to tplight.py  
1. removed '  __udp_ip = "10.0.0.130"' on line 20.  
This was causing me connection issues, and the variable is created with:  
self.__udp_ip = ip_address (line 61)  
If a valid IP is provided anyway, making this member variable declartion unrequired  
With further review, I also removed all other member variables not created within the tries.  
Except the following two:  
    __udp_port = 9999  
    __transition_period = 0  
  
2. the returned json object from the blub changes shape depending on if the light is on or off  
I added the additonal nested dict key on line 71:  
col4 = 'dft_on_state'  
Also the on/off if statement spanning lines 74 - 83  
  
  
  
# Crontolling lights via flask application.  

## 1. Review flask app python file (flask_app/flask_app.py)  

## - TPLINK 
- tpl_bulb_set (Set bulb state, colours, etc)
  
function to control bulb via an ip- takes post data  
  
example below:  
  
import requests  
requests.post("http://IP:8082/tplbulb_set/",json={"ip": "local_ip", "actions" : ["on"], "attribs": {"hsb": (240, 75, 100)}})  
  
This will set turn the bulb on, and set the hue, saturation and brightness  
Only the key 'ip' is required, "actions" and "attribs" are optional  
  
## - LIFX  
MORE INFO TO COME  
import requests  
requests.post("http://IP:8082/lifxbulb_get/",json={"Bedroom": ["power", "color"]})  
  
## 2. flask application can be ran in a docker container  
- docker_build.sh will allow named manual image builds (suits my sitch best)  
- docker_compose file could be setup to build if it fits better  
  
# local config for light control  
Within the light_sense DIR the following files contribute to controlling the bulbs state and colour:  
- common.edge.py: by default reads time till rising edge of a capacitor on gpio pin 7  
- sun_collector.py: ran by cron daily, fetches sunrise sunset times for the day  
- run_time.py: run by cron frequently, sets the colour based off time and a sunset delta. Uses light_detector for light level info and bulb comms (via the flask app).
