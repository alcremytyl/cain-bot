from typing import List, Optional
from os import environ
from pprint import pprint
from discord import Attachment, Client, File, Intents, app_commands, Interaction, guild

from .globals import TEST_GUILD, blasphemy_choices, agenda_choices, blasphemy_abilities
from .helpers import (
    ac_blashemy_ability,
    ac_describe,
    autocomplete,
    blasphemy,
    agenda,
    describe,
)


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


@client.tree.command(name="blasphemy", guild=TEST_GUILD)
@app_commands.autocomplete(name=autocomplete(blasphemy_choices))
@app_commands.autocomplete(ability=ac_blashemy_ability)
async def cmd_blasphemy(
    interaction: Interaction, name: Optional[str], ability: Optional[str]
):
    await blasphemy(interaction, name, ability)


@client.tree.command(name="agenda", guild=TEST_GUILD)
@app_commands.autocomplete(name=autocomplete(agenda_choices))
async def cmd_agenda(interaction: Interaction, name: Optional[str]):
    e = agenda(name)
    await interaction.response.send_message(embed=e)


@client.tree.command(name="describe", guild=TEST_GUILD)
@app_commands.autocomplete(what=ac_describe)
async def cmd_describe(interaction: Interaction, what: str):
    await describe(interaction, what)
