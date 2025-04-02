from pprint import pprint

from src.cogs.wiki import agenda_choices
import yaml
from src.talisman import SLASH_CHOICES, Talisman

a = Talisman("jimmy phalus", 3, 3, 1)
a._image.show()
pprint(a.to_dict())
