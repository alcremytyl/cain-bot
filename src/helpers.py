from functools import cache, lru_cache
from typing import Collection, List, Optional
from discord import Embed, Emoji, Interaction, PartialEmoji
from discord.app_commands import Choice
from discord.utils import MISSING
from fuzzywuzzy import process


from .globals import (
    ICON_URL,
    data,
    agenda_choices,
    blasphemy_choices,
    blasphemy_colors,
    blasphemy_abilities,
    describe_choices,
)

AutoCompletion = List[Choice[str]]


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


#
# ---------------------------- Command Implementations --------------------------
#


def autocomplete(choices: Collection[str]):
    async def inner(_: Interaction, current: str) -> AutoCompletion:
        return [
            Choice(name=n[0], value=n[0])
            for n in process.extract(current, choices, limit=25)
        ]

    return inner


@lru_cache(maxsize=len(agenda_choices))
def agenda(name: str | None):
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
async def blasphemy(interaction: Interaction, name: str | None, ability: str | None):
    payload = {}
    d = data["blasphemy"]

    # all blasphemies
    if name == None and ability == None:
        e = Embed()
        e.set_author(name="Blasphemies", icon_url=ICON_URL)

        for k, v in d.items():
            title = f"{emote(k,v)} **{k.upper()}**"
            desc = f'{v["description"]}'
            e.add_field(name=title, value=desc)
        payload["embed"] = e

    # specific blasphemy
    if name is not None and not ability:
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

        payload["embed"] = e

    # specific ability
    elif (name := name_from_ability(ability)) is not None:
        print("this one")
        d = d[name]
        color = blasphemy_colors[(blasphemy_choices.index(name.title())) // 3]
        e = Embed(color=color)
        e.set_author(name=name.upper())
        e.set_thumbnail(url=emote_link(d["emoji_id"]))

        for a in d["abilities"]:
            if a[0].lower() == name.lower():

                e.add_field(name=a[0].upper(), value=f"*{a[1]}*\n{a[2]}", inline=False)
                break

        payload["embed"] = e
    else:
        payload["content"] = "No such ability/blasphemy. Check your spelling."

    await interaction.response.send_message(**payload, ephemeral=True)


async def ac_blashemy_ability(interaction: Interaction, current: str) -> AutoCompletion:
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


@cache
async def describe(interaction: Interaction, target: str):
    d = data["description"]
    embed = MISSING
    content = None
    t = target.replace(": ", "-").replace(" ", "_").lower()

    if (desc := d.get(t)) is not None:
        embed = Embed(title=t.upper(), description=desc)
    else:
        content = f"No description found for `{target}`"

    await interaction.response.send_message(content=content, embed=embed)


async def ac_describe(_: Interaction, current: str) -> AutoCompletion:
    return [
        Choice(name=n[0], value=n[0])
        for n in process.extract(current, describe_choices, limit=25)
    ]
