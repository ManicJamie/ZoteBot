import json
import os
from typing import Any
import config

def save():
    with open(f"{config.path}/save.json", "w") as f:
        json.dump(SAVE_DICT, f)


if os.path.exists(f"{config.path}/save.json"):
    with open(f"{config.path}/save.json") as f:
        SAVE_DICT: dict[str, Any] = json.load(f)
else:
    SAVE_DICT: dict[str, Any] = {"pastas": {}}
    save()

PASTAS: dict[str, str] = SAVE_DICT["pastas"]
