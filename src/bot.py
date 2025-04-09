from discord import Intents, TextChannel, VoiceChannel
from discord.ext.commands import Bot, when_mentioned_or

from src.globals import COGS, OWNER_IDS, TALISMAN_CHANNEL


class CainClient(Bot):

    def __init__(self) -> None:
        intents = Intents.default()
        intents.messages = True

        super().__init__(intents=intents, command_prefix=when_mentioned_or("/"))
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

        return await super().setup_hook()


client = CainClient()


# TODO talismanize this
# NOTE: gives you a message id to work with, HUGE!!!
