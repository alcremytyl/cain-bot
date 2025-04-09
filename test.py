from contextlib import contextmanager
import yaml
from pprint import pprint

from src.cogs.talisman import TALISMAN_PATH, Talisman
from src.helpers import open_yaml


with open(TALISMAN_PATH, "r") as data:
    da = yaml.safe_load(data)
    pprint(da)
    # pprint([Talisman(**d) for d in yaml.safe_load(data)])
