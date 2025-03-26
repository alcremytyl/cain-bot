import traceback
from discord.ui import Modal, Select, TextInput, View
from discord import SelectOption, TextStyle, Interaction

from .blasphemies import Blasphemy


class ExorcistModal(Modal, title="GamesForFREAKS"):
    name = TextInput(
        label="Submit Your Character",
        placeholder="Name...",
    )

    async def on_submit(self, interaction: Interaction):
        await interaction.response.send_message(
            f"{self.children[0]} has been submitted!", ephemeral=True
        )

    async def on_error(self, interaction: Interaction, error: Exception) -> None:
        msg = "Something went wrong."

        await interaction.response.send_message(msg, ephemeral=True)

        # Make sure we know what the error actually is
        traceback.print_exception(type(error), error, error.__traceback__)


class ExorcistView(View):
    def __init__(self):
        super().__init__(timeout=180)
        # self.add_item(TextInput(label="Exorcist name", placeholder="..."))
        # self.add_item(TextInput(label="Category", placeholder="...", max_length=1))
        self.add_item(Blasphemy.as_select_opts())

    async def callback(self, interaction: Interaction):
        name: str = self.children[0].value  # type:ignore

        await interaction.response.send_message(
            f"{name} has been submitted!", ephemeral=True
        )
