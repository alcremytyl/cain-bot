from dataclasses import dataclass, field
from functools import cache
from discord import Embed, Interaction
from discord.app_commands import Choice, autocomplete, choices, command
from discord.ext.commands import Cog
from discord.ext.commands.bot import asyncio
import yaml
import Levenshtein

from src.bot import CainClient
from src.globals import CACHE_SIZE, CAIN_EMOTE, AutoCompletion
from src.helpers import Paginator, emote, emote_link
from src.transformers import StringArg


CATEGORY_MAGNITUDE_CHART = "https://github.com/alcremytyl/cain-bot/blob/master/assets/icons/~catchart.png?raw=true"


@dataclass
class Agenda:
    abilities: list[tuple[str, str]]
    emoji_id: int
    items: tuple[str, str]
    name: str
    extra: str | None = field(default=None)


@dataclass
class Blasphemy:
    abilities: list[tuple[str, str, str]]
    color: int
    description: str
    emoji_id: int
    passive: tuple[str, str]
    name: str
    extra: str | None = field(default=None)


@dataclass
class Virtue:
    name: str
    strictures: tuple[str, str]
    abilities: tuple[str, str, str, str]
    blasphemy: dict[str, str]
    extra: str | None


with open("./data/description.yaml", "r") as f:
    data = yaml.safe_load(f)
    # agendas: dict = data["agenda"]
    # blasphemies: dict = data["blasphemy"]

    agenda = [Agenda(**{"name": k, **v}) for k, v in data["agenda"].items()]
    agenda_names = [a.name for a in agenda]
    blasphemies = [Blasphemy(**{"name": k, **v}) for k, v in data["blasphemy"].items()]
    blasphemy_abilities = [i[0] for xi in blasphemies for i in xi.abilities]
    blasphemy_names = [b.name for b in blasphemies]
    catchart_data = tuple(tuple(d) for d in data["category"])
    description: dict[str, str] = data["description"]
    virtue = [Virtue(**{"name": k, **v}) for k, v in data["virtue"].items()]

    # TODO: [NEXT] try Choice[int] instead of this jabberwocky
    # if this errors, simply die
    find_agenda = lambda x: next((a for a in agenda if a.name == x.lower()))
    find_blasphemy = lambda x: next((b for b in blasphemies if b.name == x.lower()))
    find_virtue = lambda x: next((v for v in virtue if v.name == x.lower()))


class WikiCog(Cog, name="wiki"):
    def __init__(self, bot: CainClient) -> None:
        super().__init__()
        self.bot = bot

    async def _ability_cmp(self, ctx: Interaction, current: str) -> list[Choice]:
        try:
            name = ctx.namespace["name"].lower()
        except KeyError:
            name = ""

        d = (
            [a[0] for a in find_blasphemy(name).abilities]
            if name in blasphemy_names
            else blasphemy_abilities
        )

        if len(current) == 0:
            return [Choice(name=k, value=k) for k in d[:25]]

        items = tuple(
            filter(
                lambda x: x[1] > 0.6,
                sorted(
                    [(i, Levenshtein.jaro(i, current.title())) for i in d],
                    key=lambda x: x[1],
                    reverse=True,
                ),
            )
        )[:25]

        return [Choice(name=k, value=k) for (k, _) in items]

    @staticmethod
    def name_from_ability(ability: str | None) -> str | None:
        if ability is None:
            return None

        for b in blasphemies:
            for a in b.abilities:
                if ability.title() == a[0]:
                    return b.name
        return None

    # TODO: [NEXT] overview command with a view

    @command(name="blasphemy")
    @choices(name=[Choice(name=k, value=k) for k in blasphemy_names])
    @autocomplete(ability=_ability_cmp)
    async def blasphemy(
        self,
        ctx: Interaction,
        name: StringArg,
        ability: StringArg,
        ephemeral: bool = True,
    ):
        e: Embed
        if name is None and ability is None:
            e = Embed(title=f"{CAIN_EMOTE} BLASPHEMIES")
            for b in blasphemies:
                e.add_field(name=f"**{b.name.upper()}**", value=b.description)

        elif name is not None and ability is None:
            b = find_blasphemy(name)
            a = [ab[0] for ab in b.abilities]
            p = b.passive

            e = Embed(
                color=b.color,
                description=b.description,
                title=f"{CAIN_EMOTE} {name.upper()}",
            )
            e.set_thumbnail(url=emote_link(b.emoji_id))
            e.add_field(name=f"\nPASSIVE: __{p[0]}__", value=p[1], inline=False)
            e.add_field(name=f"\nABILITIES", value="- " + "\n- ".join(a), inline=False)

            if (ex := b.extra) is not None:
                e.add_field(
                    name=f"Extra Mechanic: __{ex[0]}__", value=ex[1], inline=False
                )

        elif (name := self.name_from_ability(ability)) is not None:
            ability = str(ability)  # never None

            b = find_blasphemy(name)

            tags: str = ""
            desc: str = ""

            for n, tags, desc in b.abilities:
                if n.lower() == ability.lower():
                    break
            else:
                print(f"blasphemy ability {name} not found")

            e = Embed(
                color=b.color,
                title=f"{CAIN_EMOTE} {name.upper()}::{ability.upper()}",
                description=f"*{tags}*\n\n{desc}",
            )
            e.set_thumbnail(url=emote_link(b.emoji_id))

        else:
            e = Embed(description="Dev did a fumble")

        await ctx.response.send_message(embed=e, ephemeral=ephemeral)

    @command(name="agenda")
    @choices(name=[Choice(name=k, value=k) for k in agenda_names])
    async def agenda(self, ctx: Interaction, name: StringArg, ephemeral: bool = True):
        e = Embed()

        if name is None:
            for a in agenda:
                name = emote_link(a.emoji_id) + " " + a.name.upper()
                value = f"- *{a.items[0]}*\n- **{a.items[1]}***"
                e.add_field(name=a.name.upper(), value=value)
        else:
            a = find_agenda(name)
            e.title = f"<:{name.lower()}:{a.emoji_id}> {name.upper()}"
            e.description = f"*{a.items[0]} / **{a.items[1]}***\n"
            e.set_thumbnail(url=emote_link(a.emoji_id))

            for k, v in a.abilities:
                e.add_field(name=k, value=v, inline=False)

        await ctx.response.send_message(embed=e, ephemeral=ephemeral)

    # TODO: padding, replace placeholder
    @command(name="virtue")
    @choices(name=[Choice(name=v.name, value=v.name) for v in virtue])
    async def virtue(self, ctx: Interaction, name: str, ephemeral: bool = True):
        esc = "\n"
        v = find_virtue(name)

        desc = "mucho texto"

        e = Embed(title=v.name.upper(), description=desc).set_image(
            url="https://cdn.discordapp.com/attachments/1335714104727437394/1364773830933086259/2025-04-23_21-14-25.gif?ex=680ed8ad&is=680d872d&hm=15ee57aca20b75842f5f480f59c8b503898a2532ef352171e6a4b17c303a5c38&"
        )

        e.add_field(
            name="Strictures",
            value=f"*Ignore for one roll by taking 1d3 nonlethal stress*\n\n{v.strictures[0]}\n{v.strictures[1]}\n\n",
            inline=False,
        )

        e.add_field(
            name="Bond Abilities",
            value="\n".join(
                [
                    f"`{('I' * i if i>0 else 'O'):^3}` {d}"
                    for i, d in enumerate(v.abilities)
                ]
            ),
        )

        desc = f"## Strictures\n" "## Bond Abilities\n" f"{esc.join(v.abilities)}\n"

        await ctx.response.send_message(embed=e, ephemeral=ephemeral)

    @command(name="proofreading")
    async def delete_me_when_done(self, ctx: Interaction):
        for b in blasphemies:
            for n, t, d in b.abilities:
                e = Embed(
                    title=f"{b.name.upper()}::{n.upper()}",
                    description=f"*{t}*\n\n{d}",
                    color=b.color,
                ).set_thumbnail(url=emote_link(b.emoji_id))
                await ctx.channel.send(embed=e)  # type:ignore
                await asyncio.sleep(1)

    @command(name="describe")
    @choices(info=[Choice(name=k, value=k) for k in description.keys()])
    async def describe(self, ctx: Interaction, info: str, ephemeral: bool = True):
        e = Embed(title=f"{CAIN_EMOTE} {info.upper()}", description=description[info])
        await ctx.response.send_message(embed=e, ephemeral=ephemeral)
        pass

    @command(name="category")
    async def catchart(self, ctx: Interaction, ephemeral: bool = True):
        await Paginator(catchart_data, CATEGORY_MAGNITUDE_CHART, False).setup(
            ctx, ephemeral=ephemeral
        )


async def setup(bot: CainClient):
    await bot.add_cog(WikiCog(bot))
