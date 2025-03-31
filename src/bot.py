from glob import glob
from os import environ
from discord import Intents
from discord.ext.commands import Bot

from src.globals import OWNER_IDS, TEST_GUILD


class CainClient(Bot):

    def __init__(self) -> None:
        super().__init__(intents=Intents.default(), command_prefix="/")
        self.owner_ids = OWNER_IDS

    async def on_ready(self):
        print(f"Logged in as {self.user} (ID: {self.user.id})")  # type:ignore
        print("------")

    async def setup_hook(self) -> None:
        cog_dir = "./src/cogs/"
        cogs = [g[len(cog_dir) : -3] for g in glob(cog_dir + "*.py")]

        for cog in cogs:
            await self.load_extension("src.cogs." + cog)

        await self.tree.sync(guild=TEST_GUILD)
        return await super().setup_hook()


client = CainClient()
