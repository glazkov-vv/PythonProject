import json
import os
import re


class ConfigManager:

    @staticmethod
    def init_app_mapping() -> dict:
        json_file = None
        with open("config/apps.json", "r") as f:
            json_file = f.read()
        return json.loads(json_file)
    apps_mapping: dict[str, str] = init_app_mapping()

    @classmethod
    def get_command(cls, path: str) -> str | None:
        for h in cls.apps_mapping.keys():
            regex = h
            if (re.match(regex, path)):
                return cls.apps_mapping[h].replace("$", path)

        return None
