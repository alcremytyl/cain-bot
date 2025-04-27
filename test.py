import Levenshtein
import yaml
from pprint import pprint

from src.cogs.wiki import Agenda, Blasphemy

with open("./data/description.yaml", "r") as f:
    data = yaml.safe_load(f)
    agendas: dict = data["agenda"]
    blasphemies: dict = data["blasphemy"]
    description: dict[str, str] = data["description"]
    catchart_data = tuple(tuple(d) for d in data["category"])


a = [Agenda(**{"name": k, **v}) for k, v in agendas.items()]
b = [Blasphemy(**{"name": k, **v}) for k, v in blasphemies.items()]
