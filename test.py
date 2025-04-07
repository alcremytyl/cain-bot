from typing import List
import yaml
from src.cogs.talisman import Talisman
from pprint import pprint

with open("./data/talismans.yaml", "r") as f:
    _data = yaml.safe_load(f)

pressure = _data["pressure"]
tension = _data["tension"]
talismans: List[Talisman] = []

pprint(_data["talismans"].values())
