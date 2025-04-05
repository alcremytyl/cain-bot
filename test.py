from pprint import pprint
from random import randrange

from src.cogs.wiki import agenda_choices
import yaml
from src.globals import COGS
from src.talisman import SLASH_CHOICES, Talisman, TalismansManager

with open("./data/description.yaml", "r") as f:
    _data = yaml.safe_load(f)["description"]

    marks = {
        i: (v2[0][len("sin_mark-") :].replace("_", " ").title(), v2[1].split("\n")[:-1])
        for (i, v2) in enumerate(
            ((k, v) for (k, v) in _data.items() if k.startswith("sin_mark-"))
        )
    }

    del _data

for i in range(6):
    print(marks[i])
