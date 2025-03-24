from typing import Optional
from discord import Embed, Emoji, PartialEmoji 

from globals import ICON_URL, data, agenda_choices,blasphemy_choices


def emote(name: str, d: dict):
    return f"<:{name.lower()}:{d['emoji_id']}>"


def agenda(name: Optional[str]):
    d = data["agenda"]
    if name == None:
        e = Embed()
        e.set_author(name="Agendas", icon_url=ICON_URL)

        for k, v in d.items():
            title = f"{emote(k,v)} **{k.upper()}**"
            desc = f'- {v["items"][0]}\n- **{v["items"][1]}**'
            e.add_field(name=title, value=desc)
        return e

    else:
        dt = d[name]
        e = Embed(
            # TODO: replace with CAIN logo
            title=f"{emote(name, dt)} {name.upper()}",
            description=f"## Agenda Items\n {dt['items'][0]} / **{dt['items'][1]}**\n\n## Abilities",
        )
        e.set_thumbnail(url=f"https://cdn.discordapp.com/emojis/{dt['emoji_id']}.png")

        for i in dt["abilities"]:
            e.add_field(name=i[0], value=i[1], inline=False)

        return e

# TODO: add views
def blasphemy( name: blasphemy_choices, ability: blasphemy_autocomplete) -> Embed:
    e = Embed()

    if name == None:
        e.set_author(name="Blasphemies", icon_url=ICON_URL)

        for k, v in data["blasphemy"].items():
            title = f"{emote(k,v)} **{k.upper()}**"
            desc = f'{v["description"]}'
            e.add_field(name=title, value=desc)

    elif ability == None:
        # TODO
        pass

    return e

