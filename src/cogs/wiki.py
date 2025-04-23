from functools import cache
from discord import Embed, Interaction
from discord.app_commands import Choice, autocomplete, choices, command
from discord.ext.commands import Cog
import yaml
import Levenshtein

from src.bot import CainClient
from src.globals import CACHE_SIZE, CAIN_EMOTE, AutoCompletion
from src.helpers import Paginator, emote, emote_link
from src.transformers import StringArg


CATEGORY_MAGNITUDE_CHART = "https://github.com/alcremytyl/cain-bot/blob/master/assets/icons/~catchart.png?raw=true"

with open("./data/description.yaml", "r") as f:
    data = yaml.safe_load(f)
    agendas: dict = data["agenda"]
    blasphemies: dict = data["blasphemy"]
    description: dict[str, str] = data["description"]
    catchart_data = tuple(tuple(d) for d in data["category"])
    blasphemy_abilities = [i[0] for xi in blasphemies.values() for i in xi["abilities"]]


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
            [a[0] for a in blasphemies[name.lower()]["abilities"]]
            if name in blasphemies.keys()
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

        for name, _data in blasphemies.items():
            for a in _data["abilities"]:
                if ability.title() == a[0]:
                    return name
        return None

    # TODO: overview command with a view

    @command(name="blasphemy")
    @choices(name=[Choice(name=k, value=k) for k in blasphemies.keys()])
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
            for k, v in blasphemies.items():
                e.add_field(name=f"**{k.upper()}**", value=v["description"])

        elif name is not None and ability is None:
            b = blasphemies[name]
            a = [ab[0] for ab in b["abilities"]]
            p = b["passive"]

            e = Embed(
                color=b["color"],
                description=b["description"],
                title=f"{CAIN_EMOTE} {name.upper()}",
            )
            e.set_thumbnail(url=emote_link(b["emoji_id"]))
            e.add_field(name=f"PASSIVE: __{p[0]}__", value=p[1], inline=False)
            e.add_field(name=f"ABILITIES", value="- " + "\n- ".join(a), inline=False)

            if (ex := b.get("extra")) is not None:
                e.add_field(
                    name=f"Extra Mechanic: __{ex[0]}__", value=ex[1], inline=False
                )

        elif (name := self.name_from_ability(ability)) is not None:
            ability = str(ability)  # never None

            b = blasphemies[name]

            tags: str = ""
            desc: str = ""

            for n, tags, desc in b["abilities"]:
                if name.title() == n.title():
                    break

            e = Embed(
                color=b["color"],
                title=f"{CAIN_EMOTE} {name.upper()}::{ability.upper()}",
                description=f"*{tags}*\n\n{desc}",
            )
            e.set_thumbnail(url=emote_link(b["emoji_id"]))

        else:
            e = Embed(description="Dev did a fumble")

        await ctx.response.send_message(embed=e, ephemeral=ephemeral)

    @command(name="agenda")
    @choices(name=[Choice(name=k, value=k) for k in agendas.keys()])
    async def agenda(self, ctx: Interaction, name: StringArg, ephemeral: bool = True):
        e = Embed()

        if name is None:
            for k, v in agendas.items():
                name = emote_link(v["emoji_id"]) + " " + k.upper()
                value = f"- *{v['items'][0]}*\n- **{v['items'][1]}***"
                e.add_field(name=k.upper(), value=value)
        else:
            a = agendas[name]
            e.title = f"<:{name.lower()}:{a['emoji_id']}> {name.upper()}"
            e.description = f"*{a['items'][0]} / **{a['items'][1]}***\n"
            e.set_thumbnail(url=emote_link(a["emoji_id"]))

            for k, v in a["abilities"]:
                e.add_field(name=k, value=v, inline=False)

        await ctx.response.send_message(embed=e, ephemeral=ephemeral)

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
