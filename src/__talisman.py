from typing import List
import yaml
from discord import (
    Interaction,
    TextChannel,
    VoiceChannel,
)
from discord.app_commands.commands import command
from discord.ext.commands import GroupCog

from src.bot import CainClient
from src.talisman import Talisman, TalismanMenu, TalismansManager
from src.transformers import StringArg
from src.globals import AutoCompletion


class TalismanCog(GroupCog, name="talisman"):
    def __init__(self, bot: CainClient) -> None:
        super().__init__()
        self.bot = bot
        self.manager = TalismansManager.load()
        self.messages = []

    async def ac_talisman_delete(self, current: str) -> AutoCompletion:
        return []

    @command(name="create")
    async def create(
        self, ctx: Interaction, name: str, decal: StringArg, slashes: int = 3
    ):
        msg = await self.bot.talisman_channel.send("*Creating talisman...*")
        self.messages.append(msg)

        if decal is None:
            decal = Talisman.get_random_decal()

        talisman = Talisman(name, 0, slashes, msg.id, decal)
        self.manager.add(talisman)

        await msg.edit(
            content="_ _",
            attachments=talisman.get_image(),
            view=TalismanMenu(self.manager),
        )

        await ctx.response.send_message(content="Talisman created", ephemeral=True)

    @command(name="delete")
    async def delete(self, ctx: Interaction, choice: str):
        pass

    @command(name="set_channel")
    async def set_channel(self, ctx: Interaction):
        content = str()

        if isinstance(ctx.channel, TextChannel | VoiceChannel):
            self.bot.talisman_channel = ctx.channel
            with open("./data/state.yaml", "r+") as f:
                state = yaml.safe_load(f)
                state["talisman"]["channel_id"] = ctx.channel_id
                f.seek(0)
                yaml.dump(state, f)
            content = f"Set channel to <#{ctx.channel_id}"
        else:
            content = f"Must be a text or voice channel"

        await ctx.response.send_message(content=content)


async def setup(bot: CainClient):
    await bot.add_cog(TalismanCog(bot))
