from contextlib import contextmanager
import yaml
from pprint import pprint

from src.cogs.talisman import Talisman
from src.helpers import open_yaml

Talisman("Pressure", 6, decal="pressure")
Talisman("Tension", 6, decal="tension")
