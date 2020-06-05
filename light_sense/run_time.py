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
    def exists(file_path): return True if path.exists(file_path) else False

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
    def del_if_exists(file_paths: list) -> bool:
        """
        loops through a list of Path objects, deletes the files if they exist

        Arguments:
            file_paths {list} -- [Path(mod_path, data_dir, f1), Path(mod_path, data_dir, f2)]

        Returns:
            bool -- will return True if it deletes a file from the list else False
        """
        return_bool = False
        for f in file_paths:
            if Events.exists(f):
                return_bool = True
                Events.rm([f])

        return return_bool

    @staticmethod
    def sunset_delta(ranges: list, sun_set: str, pattern=lambda i: int(1 + (i**2/2 - i/2))) -> str:
        """
        returns the sunset time with an added delta in the following format: '%H:%M:%S'

        Arguments:
            ranges {list} -- list of lists - containing 24 hour clock HOUR values
              example: [["10", "15"], ["15", "20"]] will create [["10:00:00", "15:00:00"], ["15:00:00", "20:00:00"]]
            sun_set {str} -- time as string: "20:00:00"

        Keyword Arguments:
            pattern {lambda} -- lambda to determine your delta (default: {lambdai:1+(i**2/2 - i/2)})
              default will change 1, 2, 3 into 1, 2, 4

        Returns: str -- sunstime time with delta added
        """
        ranges_max_index = len(ranges) - 1

        for index, t_range in enumerate(ranges):
            if f"{t_range[0].zfill(2)}:00:00" < sun_set <= f"{t_range[1].zfill(2)}:00:00":
                delta = pattern(index)
                break
            elif index == ranges_max_index:
                delta = 0

        sun_set_delta = (datetime.strptime(sun_set, '%H:%M:%S') +
                         timedelta(hours=delta)).strftime('%H:%M:%S')

        return sun_set_delta


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

args = parser.parse_args()
args.cut_off_hours = args.cut_off_hours.split(
    "_")  # get start and end quiet hours

# create bulb object
bulb = SetLight()

# data DIR
data_dir = Path(Path(__file__).parent).joinpath("data")
# write files names
quiet_time_f, light_on = "quiet_time", "light_on"
# transitions
day, night = "day", "night"
# possible light on files
light_files = [data_dir.joinpath(
    f"{light_on}{day}"), data_dir.joinpath(f"{light_on}{night}")]

# I want blue light for a little bit of the darkness, then red for the rest of the night
# This will vary with time of year, so below is to take this into account by adding a delta
sunset_delta = Events.sunset_delta([["18", "20"], ["17", "18"], ["15", "17"]],
                                   td().daytime[1]
                                   )

current_time = datetime.now().strftime('%H:%M:%S')

# Are we outside of cut off hours?
if not args.cut_off_hours[0] < current_time < args.cut_off_hours[1]:
    file_p = data_dir.joinpath(quiet_time_f)
    if Events.exists(file_p):
        Events.rm([file_p])
    # night or day time light
    dtime = night if current_time > sunset_delta or "00:00:00" < current_time < args.cut_off_hours[
        1] else day

    # if its dark enough, attempt to turn on the bulb
    if bulb.light_level_reached(args.bulb):
        file_p = data_dir.joinpath(f"{light_on}{dtime}")
        if not Events.exists(file_p):
            Events.write(file_p)
            # remove old day or night file
            file_p = data_dir.joinpath(
                f"{light_on}{night}" if dtime == day else f"{light_on}{day}")
            if Events.exists(file_p):
                Events.rm([file_p])
            Events.log_time_resp(f"{dtime} light on",
                                 bulb.light_on(args.bulb, dtime))
    else:  # too light, turn off bulb
        if Events.del_if_exists(light_files):
            Events.log_time_resp(f"light off", bulb.light_off(args.bulb))

else:  # cut off time reached
    file_p = data_dir.joinpath(quiet_time_f)
    if not Events.exists(file_p):
        Events.del_if_exists(light_files)
        Events.log_time_resp(f"Cut off reached. light off",
                             bulb.light_off(args.bulb))
