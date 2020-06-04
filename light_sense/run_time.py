from common.time_reader import ReadDayTimeData as td
from light_detector import SetLight
from datetime import datetime, timedelta
from argparse import ArgumentParser
from os import path, remove
from pathlib import Path

class Events:

    @staticmethod
    def write(file_path: Path): return open(file_path, "x")

    @staticmethod
    def rm(file_paths: list): [remove(f) for f in file_paths]

    @staticmethod
    def exists(file_path): True if path.exists(file_path) else False

    @staticmethod
    def log_time_resp(event: str, response: str):
        """
        prints event and response to console, captured in cron log
        Arguments:
            event {str} -- event type, on, off, cut off
            response {str} -- response from request [200, 500, 404]
        """
        print(f"'{event}' @ {datetime.now().strftime('%d/%m/%Y, %H:%M:%S')}'\n"
            f"command response: {response}"
            )

    @staticmethod
    def time_time_delta(ranges: list, sun_set: str, pattern = lambda i: 1 + (i**2/2 - i/2)):
        """
        returns the current time and the current time plus a delta as '%H:%M:%S'

        Arguments:
            ranges {list} -- list of lists - containing 24 hour clock HOUR values
              example: [["10", "15"], ["15", "20"]] will create [["10:00:00", "15:00:00"], ["15:00:00", "20:00:00"]]
            sun_set {str} -- time as string: "20:00:00"

        Keyword Arguments:
            pattern {lambda} -- lambda to determine your delta (default: {lambdai:1+(i**2/2 - i/2)})
              default will change 1, 2, 3 into 1, 2, 4

        Returns:
            current time, delta time
        """
        time_now = datetime.now()
        ranges_max_index = len(ranges) - 1

        for index, t_range in enumerate(ranges):
            if f"{t_range[0].zfill(2)}:00:00" < sun_set <= f"{t_range[1].zfill(2)}:00:00":
                delta = pattern(index)
            elif index == ranges_max_index:
                delta = 0

        return time_now.strftime('%H:%M:%S'), (time_now + timedelta(hours=delta)).strftime('%H:%M:%S')


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

# I want blue light for a little bit of the darkness, then red for the rest of the night
# This will vary with time of year, so below is to take this into account by adding a delta

# collect daylight hours
daylight_hours = td().daytime


# Get time, time delta
time_now, time_delta = Events.time_time_delta([["15", "17"], ["17", "18"], ["18", "20"]],
                                              td().daytime
                                             )

print("test")
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
# time_now = datetime.now()
# time_now_delta = (time_now + timedelta(hours=delta)).strftime('%H:%M:%S')

# create bulb object
bulb = SetLight()

args = parser.parse_args()
args.cut_off_hours = args.cut_off_hours.split("_") # get start and end quiet hours

# paths
mod_path, dir1 = Path(__file__).parent, "data"
# write files
quiet_time_f, light_on = "quiet_time", "light_on"
# transitions
day, night = "day", "night"

if not args.cut_off_hours[0] < time_now.strftime('%H:%M:%S') < args.cut_off_hours[1]:
    if path.exists(Path(mod_path, dir1, quiet_time_f)):
        remove(Path(mod_path, dir1, quiet_time_f))
    # night time light
    if time_delta > daylight_hours[1] or "00:00:00" < time_delta < args.cut_off_hours[1]:
        dtime = night
    # day time light
    else:
        dtime = day

    # if its dark enough, attempt to turn on the bulb
    if bulb.light_level_reached(args.bulb):
        if not path.exists(Path(mod_path, dir1, f"{light_on}{dtime}")):
            with open(Path(mod_path, dir1, f"{light_on}{dtime}"), "x") as _: pass
            if dtime == day:
                rm_file = f"{light_on}{night}"
            else:
                rm_file = f"{light_on}{day}"
            # remove old day or night file
            if path.exists(Path(mod_path, dir1, rm_file)):
                remove(Path(mod_path, dir1, rm_file))
            send = bulb.light_on(args.bulb, dtime)
            print(f"request for {dtime} light at: {time_now.strftime('%d/%m/%Y, %H:%M:%S')}")
            print(f"post response: {send}")
    else:  # too light, turn off bulb
        if path.exists(Path(mod_path, dir1, f"{light_on}{dtime}")):
            remove(Path(mod_path, dir1, f"{light_on}{dtime}"))
            send = bulb.light_off(args.bulb)
            print(f"bulb off at {time_now.strftime('%d/%m/%Y, %H:%M:%S')}")
            print(f"post response: {send}")

# cut off time reached
else:
    if not path.exists(Path(mod_path, dir1, quiet_time_f)):
        with open(Path(mod_path, dir1, quiet_time_f), "x") as _: pass
        for t in [day, night]:
            if path.exists(Path(mod_path, dir1, f"{light_on}{t}")):
                remove(Path(mod_path, dir1, f"{light_on}{t}"))
        send = bulb.light_off(args.bulb)
        print(f"Cut off reached. Bulb off at {time_now.strftime('%d/%m/%Y, %H:%M:%S')}")
        print(f"post response: {send}")
