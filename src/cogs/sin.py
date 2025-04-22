from dataclasses import dataclass, field
from functools import cached_property
from typing import Any
from discord import Embed, Interaction, SelectOption
from discord.app_commands import (
    Choice,
    choices,
    command,
)
from discord.ext.commands import Cog, GroupCog
from discord.ui import Select, View, select

from src.bot import CainClient
from src.helpers import open_yaml
from src.transformers import StringArg

with open_yaml("./data/sins.yaml", False) as blasphemies:
    sin_autocomplete = [Choice(name=k.title(), value=k) for k in blasphemies.keys()]

_fields = (
    "afflictions",
    "combat",
    "domains",
    "palace",
    "pressure",
    "overview",
    "severe",
    "traces",
    "trauma",
)


@dataclass
class Sin:
    afflictions: list[str]
    combat: str
    domains: dict[str, str]
    overview: str
    palace: str
    pressure: dict[str, Any]
    severe: str
    traces: dict[str, Any]
    trauma: list[str]
    url: str
    embed_map: dict[str, Embed] = field(init=False)
    name: str = field(kw_only=True)
    emoji_id: int = field(kw_only=True)

    def __post_init__(self):
        self.afflictions = [f"**{a[0]}**: {a[1]}" for a in self.afflictions]

        _afflictions = "\n".join(
            [f"{i+1}. {_t}" for (i, _t) in enumerate(self.afflictions)]
        )

        _domains = ""

        _trauma = (
            f"The Admin, as the Sin, answers the following questions, then establishes a trauma based on the truthful answers.\n\n"
            "\n".join([f"{i+1}. {_t}" for (i, _t) in enumerate(self.trauma)]) + "\n\n"
            "-# *For every question the exorcists answer, they can counter a sin’s reaction, "
            "rolling 1d3 after the sin acts. Reduce any stress sufffered by all targets by the "
            "amount on the die, and the sin immediately takes that many slashes on its execution "
            "clock from the psychic trauma, which cannot reduce it below 1.*"
        )

        self.embed_map = {
            "afflictions": Embed(description=_afflictions).set_thumbnail(url=self.url),
            "combat": Embed(description=self.combat).set_thumbnail(url=self.url),
            "domains": Embed(description=_domains).set_thumbnail(url=self.url),
            "palace": Embed(description=self.palace).set_thumbnail(url=self.url),
            "pressure": Embed(**self.pressure).set_thumbnail(url=self.url),
            "overview": Embed(description=self.overview).set_thumbnail(url=self.url),
            "severe": Embed().set_thumbnail(url=self.severe),
            "traces": Embed(**self.traces).set_thumbnail(url=self.url),
            "trauma": Embed(description=_trauma).set_thumbnail(url=self.url),
        }

    @cached_property
    def emoji(self):
        return f"<:{self.name}:{self.emoji_id}"


sins = {k.lower(): Sin(**v, name=k.lower()) for k, v in blasphemies.items()}


class SinView(View):
    def __init__(self, cog: Cog, name: str, field: str, *, timeout: float | None = 180):
        super().__init__(timeout=timeout)
        self.cog = cog
        self.name = name
        self.field = field

    sin_options = [
        SelectOption(label=s.name.lower(), emoji=s.emoji) for s in sins.values()
    ]
    field_options = [SelectOption(label=c.lower()) for c in _fields]

    @select(options=sin_options, placeholder="Select sin...")
    async def select_sin(self, ctx: Interaction, select: Select):
        # TODO
        self.name = select.values[0]
        pass

    @select(options=field_options, placeholder="Select info...")
    async def select_field(self, ctx: Interaction, select: Select):
        # TODO
        self.field = select.values[0]


class SinCog(GroupCog, name="sin"):
    def __init__(self, bot: CainClient) -> None:
        super().__init__()
        self.bot = bot

    # TODO  title + emoji as profile
    async def send_embed(
        self,
        ctx: Interaction,
        sin_key: str | None,
        field_key: str,
        ephemeral: bool = True,
    ):
        if sin_key is None:
            return await ctx.response.send_message(
                "Screech at the dev something went awful.", ephemeral=True
            )

        send = lambda em, eph: ctx.response.send_message(
            embed=em, ephemeral=eph, view=SinView(self, sin_key, field_key)
        )

        if sin_key.lower() not in sins.keys():
            return await send(
                Embed(description=f"Sin `{sin_key}` not found."), ephemeral
            )

        if field_key not in sins[sin_key].embed_map.keys():
            return await send(
                Embed(
                    description=f"No such field `{field_key}`. This shouldn't be a possible error go tell the developer."
                ),
                ephemeral,
            )

        await send(sins[sin_key].embed_map[field_key], ephemeral)

    @command()
    @choices(name=sin_autocomplete)
    async def overview(self, ctx: Interaction, name: StringArg, ephemeral: bool = True):
        if (sin := sins.get(name)) is None:
            return await ctx.response.send_message(
                f"Sin `{str(name).title()}` not implemented", ephemeral=True
            )

        await ctx.response.send_message(
            embed=sin.embed_map["overview"],
            view=SinView(self, name, "overview"),  # type:ignore
            ephemeral=ephemeral,
        )

    @command()
    @choices(name=sin_autocomplete)
    async def severe(self, ctx: Interaction, name: StringArg, ephemeral: bool = True):
        await self.send_embed(ctx, name, "severe", ephemeral)

    @command()
    @choices(name=sin_autocomplete)
    async def palace(self, ctx: Interaction, name: StringArg, ephemeral: bool = True):
        await self.send_embed(ctx, name, "palace", ephemeral)

    @command()
    @choices(name=sin_autocomplete)
    async def pressure(self, ctx: Interaction, name: StringArg, ephemeral: bool = True):
        await self.send_embed(ctx, name, "pressure", ephemeral)

    @command()
    @choices(name=sin_autocomplete)
    async def domain(self, ctx: Interaction, name: StringArg, ephemeral: bool = True):
        await self.send_embed(ctx, name, "pressure", ephemeral)

    @command()
    @choices(name=sin_autocomplete)
    async def afflictions(
        self, ctx: Interaction, name: StringArg, ephemeral: bool = True
    ):
        await self.send_embed(ctx, name, "afflictions", ephemeral=ephemeral)

    @command()
    @choices(name=sin_autocomplete)
    async def traces(self, ctx: Interaction, name: StringArg, ephemeral: bool = True):
        await self.send_embed(ctx, name, "traces", ephemeral=ephemeral)

    @command()
    @choices(name=sin_autocomplete)
    async def combat(self, ctx: Interaction, name: StringArg, ephemeral: bool = True):
        await self.send_embed(ctx, name, "combat", ephemeral=ephemeral)

    @command()
    @choices(name=sin_autocomplete)
    async def trauma(self, ctx: Interaction, name: StringArg, ephemeral: bool = True):
        await self.send_embed(ctx, name, "trauma", ephemeral=ephemeral)


async def setup(bot: CainClient):
    await bot.add_cog(SinCog(bot))
