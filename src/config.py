import json
from typing import Any
import yaml, sys
from discord import Colour

LOG_FOLDER = "logs"
LOG_PATH = "zote.log"
EMBED_COLOUR = Colour(0x79414B)

path = sys.path[0]

with open(f"{path}/precept.yaml") as f:
    precepts: list[str] = yaml.load(f, yaml.SafeLoader)

with open(f"{path}/config.json") as f:
    cfg: dict[str, Any] = json.load(f)

TOKEN = cfg.get("token", "")
ADMIN_ROLES: list[int] = cfg.get("roles", [])
OWNER_ID: int = cfg.get("owner", 0)
