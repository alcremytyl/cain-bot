from glob import glob
from os import environ
from discord import Intents
from discord.ext.commands import Bot


from .globals import TEST_GUILD


class CainClient(Bot):

    def __init__(self) -> None:
        super().__init__(intents=Intents.default(), command_prefix="/")
        self.owner_ids = [int(i) for i in environ["owner_ids"].split(" ")]
        self.talisman_channel = int(environ["talisman_channel_id"])

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
