from random import randrange
from discord import Embed, Interaction
from discord.app_commands import command
from discord.ext.commands import Cog
import yaml

from src.bot import CainClient
from src.globals import CAIN_EMOTE_LINK

with open("./data/description.yaml", "r") as f:
    _data = yaml.safe_load(f)["description"]

    marks = {
        i: (v2[0][len("sin_mark-") :].replace("_", " ").title(), v2[1].split("\n")[:-1])
        for (i, v2) in enumerate(
            ((k, v) for (k, v) in _data.items() if k.startswith("sin_mark-"))
        )
    }

    del _data


class GeneratorCog(Cog, name="generator"):
    def __init__(self, bot: CainClient) -> None:
        super().__init__()
        self.bot = bot

    @command(name="sinmark")
    async def sinmark(self, ctx: Interaction):
        embed: Embed

        if (k := randrange(6)) == 5:
            embed = (
                Embed(color=0x9F00FF)
                .set_thumbnail(url=CAIN_EMOTE_LINK)
                .add_field(name="CHOOSE", value="The rolls favor you.")
            )
        else:
            description = f"### {marks[k][0]}\n{marks[k][1][randrange(6) + 2][3:]}"
            embed = (
                Embed(color=0x9F00FF, description=description)
                .set_thumbnail(url=CAIN_EMOTE_LINK)
                .set_footer(text="\n".join(marks[k][1][:2]))
            )

        await ctx.response.send_message(embed=embed)


async def setup(bot: CainClient):
    await bot.add_cog(GeneratorCog(bot))
