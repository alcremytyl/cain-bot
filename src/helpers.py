from functools import cache, lru_cache
from typing import Collection, List, Optional
from discord import Embed, Emoji, Interaction, PartialEmoji
from discord.app_commands import Choice
from fuzzywuzzy import process

from globals import (
    ICON_URL,
    data,
    agenda_choices,
    blasphemy_choices,
    blasphemy_colors,
    blasphemy_abilities,
)


def emote(name: str, d: dict):
    return f"<:{name.lower()}:{d['emoji_id']}>"


def emote_link(id) -> str:
    return f"https://cdn.discordapp.com/emojis/{id}.png"


@cache
def name_from_ability(ability: str) -> str | None:
    for name, _data in data["blasphemy"].items():
        for a in _data["abilities"]:
            if ability.title() == a[0]:
                return name
    return None


@lru_cache(maxsize=len(agenda_choices))
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
@cache
def blasphemy(name: Optional[str], ability: Optional[str]) -> Embed:
    d = data["blasphemy"]

    # all blasphemies
    if name == None and ability == None:
        e = Embed()
        e.set_author(name="Blasphemies", icon_url=ICON_URL)

        for k, v in d.items():
            title = f"{emote(k,v)} **{k.upper()}**"
            desc = f'{v["description"]}'
            e.add_field(name=title, value=desc)
        return e

    # specific blasphemy
    if name is not None and ability == None:
        name = name.lower().strip()
        color = blasphemy_colors[(blasphemy_choices.index(name)) // 3]
        d = d[name]

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

    # specific ability
    else:
        name = str(name_from_ability(ability))
        color = blasphemy_colors[(blasphemy_choices.index(name)) // 3]
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
    try:
        name: str = interaction.namespace["name"]
    except KeyError:
        name = ""

    print("name - " + name)
    if len(name) == 0 or name.title() not in blasphemy_choices:
        choices = [a[0] for a in blasphemy_abilities.values()]

        return [Choice(name=a, value=a) for a in choices]

    return [
        Choice(name=n[0], value=n[0])
        for n in process.extract(current, blasphemy_abilities[name.lower()], limit=8)
    ]
