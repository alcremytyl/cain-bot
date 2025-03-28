from typing import List, Optional
from discord import Client, Intents, Interaction, app_commands

from src.transformers import StringArg

from .globals import TEST_GUILD, blasphemy_choices, agenda_choices
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
        
        with open("")
        self.talisman_config

    async def on_ready(self):
        print(f"Logged in as {self.user} (ID: {self.user.id})")  # type:ignore
        print("------")

    async def setup_hook(self) -> None:
        await self.tree.sync(guild=TEST_GUILD)


client = CainClient(owner_ids=[409745317114937346, 406243848554151937])
__talisman = app_commands.Group(
    name="talisman", description="collect my rupture", guild_ids=[TEST_GUILD.id]
)


@client.tree.command(name="blasphemy", guild=TEST_GUILD)
@app_commands.autocomplete(name=autocomplete(blasphemy_choices))
@app_commands.autocomplete(ability=ac_blashemy_ability)
async def __blasphemy(ctx: Interaction, name: StringArg, ability: StringArg):
    await blasphemy(ctx, name, ability)


@client.tree.command(name="agenda", guild=TEST_GUILD)
@app_commands.autocomplete(name=autocomplete(agenda_choices))
async def __agenda(ctx: Interaction, name: StringArg):
    await agenda(ctx, name)


@client.tree.command(name="describe", guild=TEST_GUILD)
@app_commands.autocomplete(what=ac_describe)
async def __describe(ctx: Interaction, what: StringArg):
    await describe(ctx, what)


@__talisman.command(name="create")
async def __talisman_create(ctx: Interaction):
    pass


@__talisman.command(name="delete")
async def __talisman_delete(ctx: Interaction):
    pass


@__talisman.command(name="set_channel")
async def __talisman_set_channel(ctx: Interaction):
    pass
