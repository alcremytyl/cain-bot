from contextlib import contextmanager
from discord.app_commands import Choice
import yaml
from pprint import pprint

from src.cogs.talisman import TALISMAN_PATH, Talisman
from src.helpers import open_yaml


with open_yaml("./data/assets.yaml") as _data:
    severe = _data["severe"]
with open_yaml("./data/sins.yaml") as _data:
    blasphemies: dict = _data
    blasphemy_autocomplete = [
        Choice(name=k.title(), value=k) for k in blasphemies.keys()
    ]


pprint(severe)
pprint(blasphemy_autocomplete)
Talisman("OGRE2", 7 + 4, decal="aa")
