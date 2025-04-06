from discord import Intents, TextChannel, VoiceChannel
import discord
from discord.ext.commands import Bot, when_mentioned_or

from src.globals import COGS, OWNER_IDS, TALISMAN_CHANNEL, TEST_GUILD


class CainClient(Bot):

    def __init__(self) -> None:
        super().__init__(
            intents=Intents.default(), command_prefix=when_mentioned_or("/")
        )
        self.owner_ids = OWNER_IDS
        self.talisman_channel: TextChannel | VoiceChannel = None  # type:ignore

    async def on_ready(self):
        print(f"Logged in as {self.user} (ID: {self.user.id})")  # type:ignore
        print("------")

        channel = await self.fetch_channel(TALISMAN_CHANNEL[1])
        if isinstance(channel, TextChannel):
            self.talisman_channel = channel
        else:
            raise ValueError("talisman_channel not set to actual channel")

    async def setup_hook(self) -> None:
        for cog in COGS:
            await self.load_extension("src.cogs." + cog)

        await self.load_extension("jishaku")

        # HACK: load config file correctly
        # await self.tree.sync(guild=discord.Object(715015385531023430))
        return await super().setup_hook()


client = CainClient()
