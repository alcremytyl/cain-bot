from discord.app_commands import Choice
from pprint import pprint

from src.cogs.sin import Sin
from src.helpers import open_yaml


with open_yaml("./data/assets.yaml") as _data:
    severe = _data["severe"]
with open_yaml("./data/sins.yaml") as _data:
    blasphemies: dict = _data
    blasphemy_autocomplete = [
        Choice(name=k.title(), value=k) for k in blasphemies.keys()
    ]

pprint({k: Sin(**v) for k, v in blasphemies.items()})
