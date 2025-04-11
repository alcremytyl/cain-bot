from discord import Embed, Interaction
from discord.app_commands import (
    Choice,
    Transform,
    Transformer,
    autocomplete,
    choices,
    command,
)
from discord.ext.commands import GroupCog

from src.bot import CainClient
from src.helpers import open_yaml
from src.transformers import StringArg

with open_yaml("./data/assets.yaml", False) as _data:
    severe = _data["severe"]
with open_yaml("./data/sins.yaml", False) as _data:
    blasphemies: dict = _data
    blasphemy_autocomplete = [
        Choice(name=k.title(), value=k) for k in blasphemies.keys()
    ]

# TODO:
"""
- impl the shits
- write overviews
- idol, hound, centipede, toad, lord


append proper thumbnail
added icons 
"""


class SinCog(GroupCog, name="sin"):
    def __init__(self, bot: CainClient) -> None:
        super().__init__()
        self.bot = bot

    blasphemies = [Choice(name=k.title(), value=k) for k in severe.keys()]

    @command()
    @choices(blasphemy=blasphemy_autocomplete)
    async def severe(self, ctx: Interaction, blasphemy: StringArg):
        if (link := severe.get(blasphemy)) is None:
            return await ctx.response.send_message("Uknown blasphemy", ephemeral=True)

        await ctx.response.send_message(embed=Embed().set_image(url=link))

    @command()
    @choices(blasphemy=blasphemy_autocomplete)
    async def palace(self, ctx: Interaction, blasphemy: StringArg):
        if (desc := blasphemies.get(blasphemy)) is not None:
            return await ctx.response.send_message(
                embed=Embed(description=desc["palace"])
            )
        pass

    @command()
    @choices(blasphemy=blasphemy_autocomplete)
    async def pressure(self, ctx: Interaction, blasphemy: StringArg):
        pass

    @command()
    @choices(blasphemy=blasphemy_autocomplete)
    async def domain(self, ctx: Interaction, blasphemy: StringArg):
        pass

    @command()
    @choices(blasphemy=blasphemy_autocomplete)
    async def affliction(self, ctx: Interaction, blasphemy: StringArg):
        pass

    @command()
    @choices(blasphemy=blasphemy_autocomplete)
    async def traces(self, ctx: Interaction, blasphemy: StringArg):
        pass

    @command()
    @choices(blasphemy=blasphemy_autocomplete)
    async def combat(self, ctx: Interaction, blasphemy: StringArg):
        # talisman size
        # attacks with
        # threats
        # complications
        pass

    @command()
    @choices(blasphemy=blasphemy_autocomplete)
    async def trauma(self, ctx: Interaction, blasphemy: StringArg):
        pass


async def setup(bot: CainClient):
    await bot.add_cog(SinCog(bot))
