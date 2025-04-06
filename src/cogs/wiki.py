from collections.abc import Collection
from functools import cache, lru_cache
from typing import Dict, List, Sequence, Tuple
from discord.ui import View, button
from discord.utils import MISSING
from fuzzywuzzy import process
from discord import ButtonStyle, Embed, Interaction
from discord.app_commands import Choice, autocomplete, command
from discord.ext.commands import Cog
import yaml

from src.bot import CainClient
from src.globals import CACHE_SIZE, CAIN_EMOTE, AutoCompletion
from src.helpers import emote, emote_link
from src.transformers import StringArg


CATEGORY_MAGNITUDE_CHART = "https://github.com/alcremytyl/cain-bot/blob/master/assets/icons/~catchart.png?raw=true"
agenda_choices: List[str] = []
blasphemy_abilities: Dict[str, List[str]] = dict()
blasphemy_choices: List[str] = []
blasphemy_colors = (0xFF0000, 0xFFC800, 0x0974F3, 0xF600FF)
describe_choices = []
catchart_data: Tuple = (
    (
        "Category Overview",
        "Sins are powerful supernatural forces, and Exorcists the weapons used to combat them. Sins may easily surpass human limits. Unfortunately, exorcists are limited by the general limits of human capabilities.\nHowever their powers, Blasphemies, are not. Much like natural disasters, both sins and exorcists are rated by Category, generally indicating their power, usually written as CAT. As each increase in category, the speed, scale, and strength of their capabilities increase drastically.\n- Category goes from 0-7, with Category 0 being general human capabilities. Anything mundane an exorcist does is usually at CAT 0.\n- Exorcists’ themselves are raed from category 1 to 5, but can sometimes push past CAT 5. This describes the capabilities of their powers.\n",
    ),
    (
        "Mundane vs supernatural",
        "Anything mundane an exorcist does to try and harm or subdue a supernatural force such as a sin is hard by default. Their capabilities and equipment are the general capabilities of a (well trained) human, usually rated at CAT 0.\nHowever, their supernatural powers are able to surpass this limit: an exorcists’s blasphemies increase in category with them.",
    ),
    (
        "Using Category",
        "Category determines the general size, strength, and scale of things in fictional terms. For example:\n- A car versus a 16 wheeler freight truck\n- A couple humans versus a whole crowd of humans\n- A shack versus a skyscraper\n- A handgun versus a bazooka\nThe Admin can use the category of something to figure out whether:\n- a roll is hard or risky for a character. A roll is typically hard or risky if the target of a power is higher category. Conversely, a roll can be less risky or hard if the target of a power is of a lower category.\n- a roll is impossible for a character given their current capabilities. For example, a character that can lift objects with their powers and is Category 4 could easily lift a car (CAT 3), but would probably find it impossible to lift a skyscraper (CAT 7). Generally tasks that are three or more categories higher than an actor are impossible for them- A roll is even required for a task, typically if it’s three or more categories lower. For example, an exorcist throwing a building at a single mundane human probably wouldn’t have to roll at all to crush them like an insect.\n- a character can do something beyond human capabilities, and to what extent These capabilities are usually listed out in short form in each power entry.\n",
    ),
)

with open("./data/description.yaml", "r") as f:
    data = yaml.safe_load(f)

    agenda_choices = list(data["agenda"].keys())

    for name, _data in data["blasphemy"].items():
        blasphemy_choices.append(name.title())
        blasphemy_abilities[name] = []

        for ability in _data["abilities"]:
            blasphemy_abilities[name].append(ability[0])

    describe_choices = [
        k.replace("-", ": ").replace("_", " ") for k in data["description"].keys()
    ]


class Paginator(View):
    def __init__(
        self, pages: Sequence[Tuple[str, str]], *, timeout: float | None = 180
    ):
        super().__init__(timeout=timeout)
        self.pages = pages
        self.current = 0

    @button(label="<", style=ButtonStyle.primary)
    async def prev(self, ctx: Interaction, *_):
        self.current -= 1
        await self.update(ctx)

    @button(label=">", style=ButtonStyle.primary)
    async def next(self, ctx: Interaction, *_):
        self.current += 1
        await self.update(ctx)

    async def update(self, ctx: Interaction):
        i = self.current % len(self.pages)
        content = "\n".join(catchart_data[i])
        await ctx.response.edit_message(
            embed=Embed(description=f"### {content}").set_image(
                url=CATEGORY_MAGNITUDE_CHART
            ),
        )


def autocomplete_generator(choices: Collection[str]):
    async def inner(_: Interaction, current: str) -> AutoCompletion:
        return __inner(current)

    @cache
    def __inner(current: str) -> AutoCompletion:
        return [
            Choice(name=n[0], value=n[0])
            for n in process.extract(current, choices, limit=25)
        ]

    return inner


@cache
def name_from_ability(ability: str | None) -> str | None:
    if ability is None:
        return None

    for name, _data in data["blasphemy"].items():
        for a in _data["abilities"]:
            if ability.title() == a[0]:
                return name
    return None


@lru_cache(maxsize=len(agenda_choices))
async def agenda(self, ctx: Interaction, name: str | None):
    d = self.data["agenda"]
    e: Embed

    if name == None:
        e = Embed(title=f"{CAIN_EMOTE} AGENDAS")

        for k, v in d.items():
            title = f"{emote(k,v)} **{k.upper()}**"
            desc = f'- {v["items"][0]}\n- **{v["items"][1]}**'
            e.add_field(name=title, value=desc)

    elif (dt := d.get(name := name.lower().strip())) is not None:
        description = (
            f"*{dt['items'][0]} / **{dt['items'][1]}***" "\n\n" "### Abilities"
        )
        e = Embed(
            title=f"{CAIN_EMOTE} {name.upper()}",
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


@cache
async def blasphemy(ctx: Interaction, name: str | None, ability: str | None):
    payload = {}
    d = data["blasphemy"]

    # all blasphemies
    if name == None and ability == None:
        e = Embed(title=f"{CAIN_EMOTE} BLASPHEMIES")

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
            title=f"{CAIN_EMOTE} {name.upper()}",
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
        e = Embed(color=color, title=f"{CAIN_EMOTE} {name.upper()}")
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


@lru_cache(maxsize=CACHE_SIZE)
async def _ac_blasphemy_ability(ctx: Interaction, current: str) -> AutoCompletion:
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


async def ac_blashemy_ability(ctx: Interaction, current: str) -> AutoCompletion:
    return await _ac_blasphemy_ability(ctx, current)


@cache
async def describe(ctx: Interaction, target: str):
    d = data["description"]
    embed = MISSING
    content = None
    t = target.replace(": ", "-").replace(" ", "_").lower()

    if (desc := d.get(t)) is not None:
        embed = Embed(title=f"{CAIN_EMOTE}{t.upper()}", description=desc)
    else:
        content = f"No description found for `{target}`"

    await ctx.response.send_message(content=content, embed=embed, ephemeral=True)


@lru_cache(maxsize=CACHE_SIZE)
def _ac_describe(current: str) -> AutoCompletion:
    return [
        Choice(name=n[0], value=n[0])
        for n in process.extract(current, describe_choices, limit=25)
    ]


async def ac_describe(_: Interaction, current: str) -> AutoCompletion:
    return _ac_describe(current)


class WikiCog(Cog, name="wiki"):
    def __init__(self, bot: CainClient) -> None:
        super().__init__()
        self.bot = bot

    @command(name="blasphemy")
    @autocomplete(name=autocomplete_generator(blasphemy_choices))
    @autocomplete(ability=ac_blashemy_ability)
    async def blasphemy(self, ctx: Interaction, name: StringArg, ability: StringArg):
        await blasphemy(ctx, name, ability)

    @command(name="agenda")
    @autocomplete(name=autocomplete_generator(agenda_choices))
    async def agenda(self, ctx: Interaction, name: StringArg):
        await agenda(ctx, name)

    @command(name="describe")
    @autocomplete(what=ac_describe)
    async def describe(self, ctx: Interaction, what: StringArg):
        await describe(ctx, what)

    @command(name="category")
    async def catchart(self, ctx: Interaction):
        view = Paginator(catchart_data)
        content = "\n".join(catchart_data[0])
        e = Embed(description=f"### {content}").set_image(url=CATEGORY_MAGNITUDE_CHART)
        await ctx.response.send_message(embed=e, view=view)


async def setup(bot: CainClient):
    await bot.add_cog(WikiCog(bot))
