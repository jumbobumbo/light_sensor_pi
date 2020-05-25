# light_sensor_pi  
LDR light sensor - flask - TPLink smart bulb control  
This readme will improve  
  
## Utilises Sunrise-Sunset api for day/night information  
https://sunrise-sunset.org/api  
  
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

2. the returned json object from the blub changes shape depending on if the light is on or off  
I added the additonal nested dict key on line 71:  
col4 = 'dft_on_state'  
Also the on/off if statement spanning lines 74 - 83  
