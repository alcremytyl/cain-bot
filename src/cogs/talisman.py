from typing import List
from discord import (
    File,
    Interaction,
    Message,
)
from discord.app_commands.commands import guild_only, command
from discord.ext.commands import GroupCog

from src.bot import CainClient
from src.talisman import Talisman, TalismansManager
from src.transformers import StringArg


@guild_only()
class TalismanCog(GroupCog, name="talisman"):
    def __init__(self, bot: CainClient) -> None:
        super().__init__()
        self.bot = bot
        self.manager = TalismansManager.load()
        # TODO: some on_ready load
        self.messages: List[Message] = []

    async def talisman_create(
        self,
        ctx: Interaction,
        name: str,
        slashes: int,
        decal: StringArg,
    ):
        ch = self.bot.talisman_channel
        msg = await ch.send("*Creating talisman...*")
        self.messages.append(msg)

        if decal is None:
            decal = Talisman.get_random_decal()

        talisman = Talisman(name, 0, slashes, msg.id, decal)
        self.manager.add(talisman)

        with open(talisman.get_image_fp(), "rb") as f:
            await msg.edit(content="_ _", attachments=[File(f, "talisman.png")])

        await ctx.response.send_message(content="Talisman created", ephemeral=True)

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
