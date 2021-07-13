import json
from os.path import exists
from typing import Dict


class Config:
    def __init__(self) -> None:
        if exists("config.json"):
            with open("config.json") as F:
                pass
                self._json_data = json.load(F)
        else:
            with open("config.json", "w") as fp:
                json.dump(dict(self._json_data), fp)

    @property
    def configs(self) -> Dict:
        """Returns all config properties in a dictionary"""
        return self._json_data
