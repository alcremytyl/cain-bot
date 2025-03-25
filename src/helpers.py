from typing import Collection, List, Optional
from discord import Embed, Emoji, Interaction, PartialEmoji
from discord.app_commands import Choice
from fuzzywuzzy import process

from globals import ICON_URL, data, agenda_choices, blasphemy_choices, blasphemy_colors


def emote(name: str, d: dict):
    return f"<:{name.lower()}:{d['emoji_id']}>"


def emote_link(id) -> str:
    return f"https://cdn.discordapp.com/emojis/{id}.png"


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
        e.set_thumbnail(url=emote_link(dt["emoji_id"]))

        for i in dt["abilities"]:
            e.add_field(name=i[0], value=i[1], inline=False)

        return e


# TODO:
# add views
# make it shit out info of the ability itself
def blasphemy(name: Optional[str], ability: Optional[str]) -> Embed:
    d = data["blasphemy"]
    if name == None:
        e = Embed()
        e.set_author(name="Blasphemies", icon_url=ICON_URL)

        for k, v in d.items():
            title = f"{emote(k,v)} **{k.upper()}**"
            desc = f'{v["description"]}'
            e.add_field(name=title, value=desc)
        return e

    color = blasphemy_colors[(blasphemy_choices.index(name)) // 3]
    name = name.lower().strip()
    d = d[name]

    if ability == None:
        passive = d["passive"]
        abilities = [a[0] for a in d["abilities"]]
        extra = d.get("extra")

        e = Embed(
            color=color,
            description=d["description"],
        )
        e.set_author(name=name.upper())
        e.set_thumbnail(url=emote_link(d["emoji_id"]))
        e.add_field(name=f"PASSIVE: __{passive[0]}__", value=passive[1], inline=False)
        e.add_field(name="ABILITIES", value="- " + "\n- ".join(abilities), inline=True)

        if extra is not None:
            e.add_field(name=f"Extra Mechanic: __{extra[0]}__", value=extra[1])

        return e

    else:
        e = Embed(color=color)
        e.set_author(name=name.upper())
        e.set_thumbnail(url=emote_link(d["emoji_id"]))

        for a in d["abilities"]:
            e.add_field(name=a[0].upper(), value=f"*{a[1]}*\n{a[2]}", inline=False)

        return e


def autocomplete(choices: Collection[str]):
    async def inner(_: Interaction, current: str) -> List[Choice[str]]:
        return [
            Choice(name=n[0], value=n[0])
            for n in process.extract(current, choices, limit=16)
        ]

    return inner


async def blasphemy_autocomplete(
    interaction: Interaction, current: str
) -> List[Choice[str]]:
    name: str = interaction.namespace["name"]

    if len(name) <= 0 and name.title() not in blasphemy_choices:
        return []

    choices = [a[0] for a in data["blasphemy"][name.lower()]["abilities"]]

    return [
        Choice(name=n[0], value=n[0])
        for n in process.extract(current, choices, limit=8)
    ]
