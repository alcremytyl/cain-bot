from discord import Embed, Interaction, SelectOption
from discord.app_commands import (
    Choice,
    choices,
    command,
)
from discord.ext.commands import Cog, GroupCog
from discord.ui import Select, View, select

from src.bot import CainClient
from src.helpers import Paginator, open_yaml
from src.transformers import StringArg

with open_yaml("./data/assets.yaml", False) as _data:
    severe = _data["severe"]
with open_yaml("./data/sins.yaml", False) as _data:
    blasphemies: dict = _data
    sin_autocomplete = [Choice(name=k.title(), value=k) for k in blasphemies.keys()]

# TODO:
"""
- impl the shits
- write overviews
- idol, hound, centipede, toad, lord
"""


class SinCog(GroupCog, name="sin"):
    def __init__(self, bot: CainClient) -> None:
        super().__init__()
        self.bot = bot

    @property
    def view(self):
        # very dumb idea that works
        class SinView(View):
            def __init__(self, cog: Cog, *, timeout: float | None = 180):
                super().__init__(timeout=timeout)
                self.cog = cog

            options = [
                SelectOption(label=c.name, description=c.description)
                for c in self.walk_app_commands()
            ]

            @select(options=options)
            async def select_sin(self, ctx: Interaction, select: Select):
                # TODO: generate mapping of embeds for every sin on startup and use them for this mf
                return await ctx.response.send_message("ya")

        return SinView(self)

    @command()
    @choices(name=sin_autocomplete)
    async def overview(self, ctx: Interaction, name: StringArg, ephemeral: bool = True):
        await ctx.response.send_message("canard so awesome", view=self.view)

    @command()
    @choices(name=sin_autocomplete)
    async def severe(self, ctx: Interaction, name: StringArg, ephemeral: bool = True):
        if (link := severe.get(name)) is None:
            return await ctx.response.send_message("Uknown sin", ephemeral=True)

        await ctx.response.send_message(
            embed=Embed().set_image(url=link), ephemeral=ephemeral
        )

    @command()
    @choices(name=sin_autocomplete)
    async def palace(self, ctx: Interaction, name: StringArg, ephemeral: bool = True):
        if (desc := blasphemies.get(name)) is None:
            return await ctx.response.send_message("Unknown sin", ephemeral=True)

        await ctx.response.send_message(
            embed=Embed(description=desc["palace"]).set_thumbnail(url=desc["url"]),
            ephemeral=ephemeral,
        )

    @command()
    @choices(name=sin_autocomplete)
    async def pressure(self, ctx: Interaction, name: StringArg, ephemeral: bool = True):
        if (desc := blasphemies.get(name)) is None:
            return await ctx.response.send_message("Unknown sin", ephemeral=True)

        await ctx.response.send_message(
            embed=Embed(
                title=desc["pressure"]["name"],
                description=desc["pressure"]["description"],
            ).set_thumbnail(url=desc["url"]),
            ephemeral=ephemeral,
        )

    @command()
    @choices(name=sin_autocomplete)
    async def domain(self, ctx: Interaction, name: StringArg, ephemeral: bool = True):
        if (desc := blasphemies.get(name)) is None:
            return await ctx.response.send_message("Unknown sin", ephemeral=True)

        await Paginator(desc["domains"], desc["url"], True).setup(
            ctx, ephemeral=ephemeral
        )

    @command()
    @choices(name=sin_autocomplete)
    async def afflictions(
        self, ctx: Interaction, name: StringArg, ephemeral: bool = True
    ):
        if (desc := blasphemies.get(name)) is None:
            return await ctx.response.send_message("Unknown sin", ephemeral=True)

        await ctx.response.send_message(
            embed=Embed(description=desc["afflictions"]).set_thumbnail(url=desc["url"]),
            ephemeral=ephemeral,
        )

    @command()
    @choices(name=sin_autocomplete)
    async def traces(self, ctx: Interaction, name: StringArg, ephemeral: bool = True):
        if (desc := blasphemies.get(name)) is None:
            return await ctx.response.send_message("Unknown sin", ephemeral=True)

        await ctx.response.send_message(
            embed=Embed(
                title=desc["traces"]["name"], description=desc["traces"]["description"]
            ).set_thumbnail(url=desc["url"]),
            ephemeral=ephemeral,
        )

    @command()
    @choices(name=sin_autocomplete)
    async def combat(self, ctx: Interaction, name: StringArg, ephemeral: bool = True):
        if (desc := blasphemies.get(name)) is None:
            return await ctx.response.send_message("Unknown sin", ephemeral=True)

        await ctx.response.send_message(
            embed=Embed(description=desc["combat"]).set_thumbnail(url=desc["url"]),
            ephemeral=ephemeral,
        )

    @command()
    @choices(name=sin_autocomplete)
    async def trauma(self, ctx: Interaction, name: StringArg, ephemeral: bool = True):
        if (desc := blasphemies.get(name)) is None:
            return await ctx.response.send_message("Unknown sin", ephemeral=True)
        t = "\n".join([f"{i+1}. {_t}" for (i, _t) in enumerate(desc["trauma"])])

        content = (
            "The Admin, as the ogre, answers the following questions, then establishes a trauma based on the truthful answers.\n\n"
            f"**{t}**\n\n"
            "-# *For every question the exorcists answer, they can counter a sin’s reaction, rolling 1d3 after the sin acts. Reduce any stress sufffered by all targets by the amount on the die, and the sin immediately takes that many slashes on its execution clock from the psychic trauma, which cannot reduce it below 1.*"
        )
        await ctx.response.send_message(
            embed=Embed(description=content).set_thumbnail(url=desc["url"]),
            ephemeral=ephemeral,
        )


SinCog.walk_app_commands


async def setup(bot: CainClient):
    await bot.add_cog(SinCog(bot))
