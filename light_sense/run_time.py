from common.time_reader import ReadDayTimeData as td
from light_detector import SetLight
from datetime import datetime, timedelta
from argparse import ArgumentParser
from os import path, remove
from pathlib import Path

# move to appropriate place
mod_path, dir1, quiet_time_f = Path(__file__).parent, "data", "quiet_time.txt"

# cmd line args
parser = ArgumentParser(description="Turns a bulb off or on depending on time/light level",
                        usage="run_time.py bulb cut_off_time\n"
                              "example args:'office' '02:00:00_08:00:00'"
                        )

parser.add_argument("bulb",
                    type=str,
                    help="name of bulb, in config/conf.json"
                    )
parser.add_argument("cut_off_hours",
                    type=str,
                    help="quiet hours for bulb, regardless of light level\n"
                         "seperated_by_underscores. example: 02:00:00_08:00:00"
                    )

# collect args
args = parser.parse_args()
# split quiet hours
args.cut_off_hours = args.cut_off_hours.split("_")

# collect daylight hours
daylight_hours = td().daytime

# I want blue light for a little bit of the darkness, then red for the rest of the night
# This will vary with time of year, so below is to take this into account by adding a delta

# amend for changing sunset hours - add delta
if "15:00:00" < daylight_hours[1] <= "17:00:00":
    delta = 4
elif "17:00:00" < daylight_hours[1] <= "18:00:00":
    delta = 2
elif "18:00:00" < daylight_hours[1] <= "20:00:00":
    delta = 1
else:
    delta = 0

# collect time now
time_now = datetime.now()
time_now_delta = (time_now + timedelta(hours=delta)).strftime('%H:%M:%S')

# bulb object
bulb = SetLight()

if not args.cut_off_hours[0] < time_now.strftime('%H:%M:%S') < args.cut_off_hours[1]:
    if path.exists(Path(mod_path, dir1, quiet_time_f)):
        remove(Path(mod_path, dir1, quiet_time_f))
    # night time light
    if time_now_delta > daylight_hours[1] or "00:00:00" < time_now_delta < args.cut_off_hours[1]:
        dtime = "night"
    # day time light
    else:
        dtime = "day"

    # if its dark enough, attempt to turn on the bulb
    if bulb.light_level_reached(args.bulb):
        send = bulb.light_on(args.bulb, dtime)
        print(f"request for {dtime} light at: {time_now.strftime('%d/%m/%Y, %H:%M:%S')}")
    else:  # make sure its off - improve to read value first in next release?
        send = bulb.light_off(args.bulb)
        print(f"bulb off at {time_now.strftime('%d/%m/%Y, %H:%M:%S')}")

    print(f"post response: {send}")

# cut off time reached
else:
    if not path.exists(Path(mod_path, dir1, quiet_time_f)):
        with open(Path(mod_path, dir1, quiet_time_f), "x") as _: pass
        send = bulb.light_off(args.bulb)
        print(f"Cut off reached. Bulb off at {time_now.strftime('%d/%m/%Y, %H:%M:%S')}")
        print(f"post response: {send}")
