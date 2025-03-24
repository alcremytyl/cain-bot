from typing import Optional
from discord import Embed, Emoji, PartialEmoji

# HACK: temporary
ICON_URL = "https://cdn.discordapp.com/attachments/1112259815905951780/1353591695446380555/image.png?ex=67e23600&is=67e0e480&hm=3b0bfd5961a10f1c8a60418606f66b374286cdcdb48597fcacf0660ec9da63d0&"


def emote(name: str, d: dict):
    return f"<:{name.lower()}:{d['emoji_id']}>"


# TODO: add views
def blasphemy(data: dict, name: Optional[str], ability: Optional[str]) -> Embed:
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


def agenda(data: dict, name: Optional[str]):
    d = data["agenda"]
    if name == None:
        e = Embed()
        e.set_author(name="Agendas", icon_url=ICON_URL)

        for k, v in d.items():
            title = f"{emote(k,v)} **{k.upper()}**"
            desc = f'-{v["items"][0]}\n- **{v["items"][1]}**'
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
