from typing import List, Optional
import discord
from os import environ
import tomllib
from pprint import pprint
from discord import Attachment, Client, File, Intents, app_commands, Interaction, guild

from helpers import blasphemy, agenda
from ui import ExorcistView

with open("./assets/data.toml", "rb") as f:
    data = tomllib.load(f)


TEST_GUILD = discord.Object(int(environ["test_guild"]))


class CainClient(Client):
    def __init__(self, owner_ids: List[int]) -> None:
        intents = Intents.default()
        super().__init__(intents=intents)
        self.owner_ids = owner_ids
        self.tree = app_commands.CommandTree(self)

    async def on_ready(self):
        print(f"Logged in as {self.user} (ID: {self.user.id})")  # type:ignore
        print("------")

    async def setup_hook(self) -> None:
        await self.tree.sync(guild=TEST_GUILD)


client = CainClient(owner_ids=[409745317114937346, 406243848554151937])


@client.tree.command(name="register-exorcist", guild=TEST_GUILD)
async def register(
    interaction: Interaction, name: str, category: int, profile: Optional[Attachment]
):
    # await interaction.response.send_modal(ExorcistModal())
    await interaction.response.send_message("ok")


# TODO: transformers
@client.tree.command(name="blasphemy", guild=TEST_GUILD)
async def cmd_blasphemy(
    interaction: Interaction, name: Optional[str], ability: Optional[str]
):
    e = blasphemy(data, name, ability)
    await interaction.response.send_message(embed=e, ephemeral=True)


@client.tree.command(name="agenda", guild=TEST_GUILD)
async def cmd_agenda(interaction: Interaction, name: Optional[str]):
    e = agenda(data, name)
    await interaction.response.send_message(embed=e)


client.run(environ["discord_token"])
