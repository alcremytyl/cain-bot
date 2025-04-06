from discord import Interaction
import discord
from discord.app_commands import command
from discord.ext import commands
from discord.ext.commands import Cog

from src.bot import CainClient
from src.globals import COGS


class MaintenanceCog(Cog, name="maintenance"):
    def __init__(self, bot: CainClient) -> None:
        self.bot = bot
        super().__init__()

    @command(name="sync")
    @commands.is_owner()
    async def sync(self, ctx: Interaction):
        await ctx.response.send_message("Syncing...", ephemeral=True)

        for cog in COGS:
            await self.bot.reload_extension("src.cogs." + cog)

        await self.bot.tree.sync(guild=discord.Object(715015385531023430))
        await ctx.edit_original_response(content="Done!")

    @command(name="cog-reload")
    @commands.is_owner()
    async def reload(self, ctx: Interaction):
        for cog in COGS:
            await self.bot.reload_extension("src.cogs." + cog)

        await ctx.response.send_message("done", ephemeral=True)


async def setup(bot: CainClient):
    await bot.add_cog(MaintenanceCog(bot))
