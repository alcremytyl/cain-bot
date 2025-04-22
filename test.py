import Levenshtein
import yaml
from pprint import pprint

with open("./data/description.yaml", "r") as f:
    data = yaml.safe_load(f)
    agendas: dict = data["agenda"]
    blasphemies: dict = data["blasphemy"]
    description: dict[str, str] = data["description"]
    catchart_data = tuple(tuple(d) for d in data["category"])


def name_from_ability(ability: str | None) -> str | None:
    if ability is None:
        return None

    for name, _data in data["blasphemy"].items():
        for a in _data["abilities"]:
            if ability.title() == a[0]:
                return name
    return None


print(name_from_ability("sabre"))
