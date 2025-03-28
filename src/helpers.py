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


def emote(name: str, d: dict):
    return f"<:{name.lower()}:{d['emoji_id']}>"


def emote_link(id) -> str:
    return f"https://cdn.discordapp.com/emojis/{id}.png"


AutoCompletion = List[Choice[str]]

__CACHE_SIZE = 256
__CAIN_EMOTE_DATA = ("cain", 1354946062032437440)
__CAIN_EMOTE = f"<:{__CAIN_EMOTE_DATA[0]}:{__CAIN_EMOTE_DATA[1]}>"
__CAIN_EMOTE_LINK = emote_link(__CAIN_EMOTE_DATA[1])


@cache
def name_from_ability(ability: str | None) -> str | None:
    if ability is None:
        return None

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
        return __inner(current)

    @cache
    def __inner(current: str) -> AutoCompletion:
        return [
            Choice(name=n[0], value=n[0])
            for n in process.extract(current, choices, limit=25)
        ]

    return inner


@lru_cache(maxsize=len(agenda_choices))
async def agenda(ctx: Interaction, name: str | None):
    d = data["agenda"]
    e: Embed

    if name == None:
        e = Embed(title=f"{__CAIN_EMOTE} AGENDAS")

        for k, v in d.items():
            title = f"{emote(k,v)} **{k.upper()}**"
            desc = f'- {v["items"][0]}\n- **{v["items"][1]}**'
            e.add_field(name=title, value=desc)

    elif (dt := d.get(name := name.lower().strip())) is not None:
        description = (
            f"*{dt['items'][0]} / **{dt['items'][1]}***" "\n\n" "### Abilities"
        )
        e = Embed(
            title=f"{__CAIN_EMOTE} {name.upper()}",
            description=description,
        )
        e.set_thumbnail(url=emote_link(dt["emoji_id"]))

        for i in dt["abilities"]:
            e.add_field(name=i[0], value=i[1], inline=False)
    else:
        e = Embed(
            title="Error!", description=f"No such agenda `{name}` in this campaign."
        )

    await ctx.response.send_message(embed=e, ephemeral=True)


# TODO:
# add views
# make it shit out info of the ability itself
@cache
async def blasphemy(ctx: Interaction, name: str | None, ability: str | None):
    payload = {}
    d = data["blasphemy"]

    # all blasphemies
    if name == None and ability == None:
        e = Embed(title=f"{__CAIN_EMOTE} BLASPHEMIES")

        for k, v in d.items():
            title = f"{emote(k,v)} **{k.upper()}**"
            desc = f'{v["description"]}'
            e.add_field(name=title, value=desc)
        payload["embed"] = e

    # specific blasphemy
    elif name is not None:
        color = blasphemy_colors[(blasphemy_choices.index(name.title())) // 3]
        d = d[name]

        passive = d["passive"]
        abilities = [a[0] for a in d["abilities"]]
        extra = d.get("extra")

        e = Embed(
            color=color,
            description=d["description"],
            title=f"{__CAIN_EMOTE} {name.upper()}",
        )
        e.set_thumbnail(url=emote_link(d["emoji_id"]))
        e.add_field(name=f"PASSIVE: __{passive[0]}__", value=passive[1], inline=False)
        e.add_field(name="ABILITIES", value="- " + "\n- ".join(abilities), inline=True)

        if extra is not None:
            e.add_field(name=f"Extra Mechanic: __{extra[0]}__", value=extra[1])

        payload["embed"] = e

    # specific ability
    elif (name := name_from_ability(ability)) is not None:
        ability = str(ability)  # not None due to condition
        d = d[name]
        color = blasphemy_colors[(blasphemy_choices.index(name.title())) // 3]
        e = Embed(color=color, title=f"{__CAIN_EMOTE} {name.upper()}")
        e.set_thumbnail(url=emote_link(d["emoji_id"]))

        for a in list(d["abilities"]):
            if a[0].lower() == ability.lower():

                e.add_field(name=a[0].upper(), value=f"*{a[1]}*\n{a[2]}", inline=False)
                break
        else:
            e.add_field(
                name="Error!",
                value="Probably typo'd on the ability name. This shouldn't be possible.",
            )

        payload["embed"] = e
    else:
        payload["content"] = "No such ability/blasphemy. Check your spelling."

    await ctx.response.send_message(**payload, ephemeral=True)


async def ac_blashemy_ability(ctx: Interaction, current: str) -> AutoCompletion:
    return await __ac_blasphemy_ability(ctx, current)


@lru_cache(maxsize=__CACHE_SIZE)
async def __ac_blasphemy_ability(ctx: Interaction, current: str) -> AutoCompletion:
    try:
        name: str = ctx.namespace["name"]
    except KeyError:
        name = ""

    if name:
        choices = blasphemy_abilities[name.lower()]
    else:
        choices = [a[0] for a in blasphemy_abilities.values()]

    return [
        Choice(name=n[0], value=n[0])
        for n in process.extract(current, choices, limit=25)
    ]


@cache
async def describe(ctx: Interaction, target: str):
    d = data["description"]
    embed = MISSING
    content = None
    t = target.replace(": ", "-").replace(" ", "_").lower()

    if (desc := d.get(t)) is not None:
        embed = Embed(title=t.upper(), description=desc)
    else:
        content = f"No description found for `{target}`"

    await ctx.response.send_message(content=content, embed=embed)


async def ac_describe(_: Interaction, current: str) -> AutoCompletion:
    return await __ac_describe(current)


@lru_cache(maxsize=__CACHE_SIZE)
async def __ac_describe(current: str) -> AutoCompletion:
    return [
        Choice(name=n[0], value=n[0])
        for n in process.extract(current, describe_choices, limit=25)
    ]
