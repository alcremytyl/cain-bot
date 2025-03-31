from typing import List
from discord import (
    CategoryChannel,
    File,
    ForumChannel,
    Interaction,
    Message,
    NotFound,
)
from discord.app_commands.commands import guild_only, command
from discord.ext.commands import GroupCog

from src.bot import CainClient
from src.globals import TALISMAN_CHANNEL
from src.talisman import Talisman, TalismansManager
from src.transformers import StringArg


@guild_only()
class TalismanCog(GroupCog, name="talisman"):
    def __init__(self, bot: CainClient) -> None:
        super().__init__()
        self.bot = bot
        self.manager = TalismansManager.load()
        self.messages: List[Message] = []
        self.channel = self.bot.fetch_channel(TALISMAN_CHANNEL[1])

    async def talisman_create(
        self,
        ctx: Interaction,
        name: str,
        slashes: int,
        decal: StringArg,
    ):
        try:
            # guild = await self.bot.fetch_guild(715015385531023430)
            # channel = await guild.fetch_channel(1356081547576610836)
            # if isinstance(channel, (CategoryChannel, ForumChannel)):
            #     raise ValueError("channel id was not set to an actual channel")
            #
            # if decal is None:
            #     decal = Talisman.get_random_decal()
            #
            # if self.manager.add(talisman):
            #     msg = await channel.send("*Creating talisman...*")
            #     talisman = Talisman(name, 0, slashes, msg.id, decal)
            #     content = "Talisman already exists."
            #
            #     with open(talisman.get_image_fp(), "rb") as f:
            #         await msg.edit(content="_ _", attachments=[File(f, "talisman.png")])
            # else:
            #     content = "Created talisman"
            #
            # await ctx.response.send_message(content=content, ephemeral=True)
            await ctx.response.send_message("WIP", ephemeral=True)

        except NotFound:
            print("NOT FOUND DO SOMETHI8NG ABOUT IT")

    @command(name="create")
    async def create(
        self, ctx: Interaction, name: str, decal: StringArg, slashes: int = 3
    ):
        await self.talisman_create(ctx, name, slashes, decal)

    @command(name="delete")
    async def delete(self, ctx: Interaction):
        pass

    @command(name="set_channel")
    async def set_channel(self, ctx: Interaction):
        pass


async def setup(bot: CainClient):
    await bot.add_cog(TalismanCog(bot))
