from discord import Intents, Interaction, Message, TextChannel, TextInput, VoiceChannel
from discord.app_commands import context_menu
from discord.ext.commands import Bot, when_mentioned_or
from discord.ui import Modal, TextInput

from src.globals import COGS, OWNER_IDS, TALISMAN_CHANNEL, TEST_GUILD


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


class TestModal(Modal, title="yearn for the mines"):
    text = TextInput(label="testing")

    async def on_submit(self, interaction: Interaction):
        await interaction.response.send_message("yeah", ephemeral=True)
        return await super().on_submit(interaction)


@client.tree.context_menu(name="set talisman")
async def set_talisman(ctx: Interaction, m: Message):
    if len(m.attachments) != 1:
        return await ctx.response.send_message("Not a talisman")
    if not m.attachments[0].filename.endswith("talisman.png"):
        return await ctx.response.send_message("Not a talisman")

    key = m.attachments[0].filename.rsplit("--")[-1].replace("_", " ")

    a = await ctx.response.send_modal(TestModal())

    # TODO talismanize this
    # NOTE: gives you a message id to work with, HUGE!!!
    print(a)
    print(a.__slots__)

    # await ctx.response.defer(thinking=False)
