from discord import Interaction
from discord.app_commands import command
from discord.ext import commands
from discord.ext.commands import Cog

from src.bot import CainClient


class MaintenanceCog(Cog, name="maintenance"):
    def __init__(self, bot: CainClient) -> None:
        self.bot = bot
        super().__init__()

    @command(name="sync")
    @commands.is_owner()
    async def sync(self, ctx: Interaction):
        await ctx.response.send_message("Syncing...", ephemeral=True)
        await self.bot.tree.sync()
        await ctx.edit_original_response(content="Done!")


async def setup(bot: CainClient):
    await bot.add_cog(MaintenanceCog(bot))
