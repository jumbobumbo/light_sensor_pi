from json import load
from pathlib import Path
from re import findall

# Path to parent DIR
mod_path = Path(__file__).parent

class ReadDayTimeData:

    def __init__(self, daytime_json="daytime_data.json"):
        self.daytime = daytime_json

    @property
    def daytime(self):
        return self.__daytime_data

    @daytime.setter
    def daytime(self, daytime_json):
        with open(Path(mod_path.parent, "data", daytime_json), "r") as f:
            data = load(f)

        # fetch the time specific values
        self.__daytime_data = findall(r"T(.*?)\+", str(data))
        return self.__daytime_data

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}{self.daytime}"

if __name__ == "__main__":
    time = ReadDayTimeData()
    print(time.daytime)