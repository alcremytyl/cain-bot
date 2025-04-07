from discord import ButtonStyle, File, Interaction
from discord.app_commands import command
from discord.ext.commands import GroupCog
from discord.ui import Button, View, button
import yaml
from src.bot import CainClient

from glob import glob
import os
from dataclasses import dataclass, field
import random
from typing import Dict, List

from PIL import ImageDraw, ImageFont
from PIL.Image import Image, new as pil_new, Resampling, open as pil_open

DECAL_RANDRANGE = 14
TALISMAN_TEMPLATE_PATH = "./assets/talisman.png"
TALISMAN_FONT_PATH = "./assets/Apex-Black.ttf"
SLASH_CHOICES = glob("./assets/slashes/*.png")
FONT = ImageFont.truetype(TALISMAN_FONT_PATH, size=50)


# TODO
"""
- context menu
- setup
- make sure it's all good with the yaml
"""


@dataclass
class Talisman:
    name: str
    slashes: int
    current: int = field(default=0)
    decal: str = field(default="")
    generate_images: bool = field(default=True)

    def __post_init__(self):
        if self.decal == "":
            self.decal = str(random.randrange(DECAL_RANDRANGE))

        if self.slashes not in range(1, 25):
            raise ValueError("Maximum talisman range must be within 1 - 24")

        self.name = self.name.title()

        if self.generate_images:
            self.generate()

        with open("./data/talismans.yaml", "r") as f:
            _data = yaml.safe_load(f)
            _data["talismans"][self.name] = self.as_dict()

        with open("./data/talismans.yaml", "w") as f:
            yaml.safe_dump(_data, f)

    def as_dict(self) -> Dict:
        return {
            "current": self.current,
            "decal": self.decal,
            "name": self.name,
            "slashes": self.slashes,
        }

    def generate(self) -> Image:
        # cleanup, assumes no dupes in use
        self.delete()

        image = pil_open(TALISMAN_TEMPLATE_PATH)
        img_pos_rc = (image.width, image.height // 2)

        decal = pil_open(f"./assets/decals/{self.decal}.png")
        decal.thumbnail((100, 100))
        image.paste(decal, (14, (image.height - 90) // 2), decal)

        text = pil_new("RGBA", image.size, (255, 255, 255, 0))
        draw = ImageDraw.Draw(text)
        draw.text(img_pos_rc, self.name, (0, 0, 0, 204), FONT, "rm")
        draw.text((162, 56), str(self.slashes), (255, 255, 255, 225), FONT, "mm")
        image.paste(text, text)

        image.save(f"./tmp/{self.name}-0.png")

        for i in range(1, self.slashes):
            fp = random.choice(SLASH_CHOICES)
            slash = pil_open(fp).rotate(random.randrange(-5, 5), Resampling.BICUBIC)
            pos = (24 * (i + 8), (image.height - slash.height) // 2)
            image.paste(slash, pos, slash)
            image.save(f"./tmp/{self.name}-{i}.png")

        fp = random.choice(SLASH_CHOICES)
        slash = pil_open(fp).rotate(random.randrange(-5, 5), Resampling.BICUBIC)
        pos = (24 * (self.slashes + 8), (image.height - slash.height) // 2)
        image.paste(slash, pos, slash)
        resolve = pil_open("./assets/decals/resolved.png")

        image.paste(resolve, (-28, -17), resolve)
        image.save(f"./tmp/{self.name}-{self.slashes}.png")

        return image

    def delete(self):
        for fp in glob(f"./tmp/{self.name}-*.png"):
            os.remove(fp)

    def get_image(self) -> File:
        fp = f"./tmp/{self.name}-{self.current}.png"

        if not os.path.isfile(fp):
            raise ValueError(f"No such file {fp}")

        return File(fp=fp, filename="talisman.png")


class TalismanView(View):
    def __init__(self, t: Talisman):
        super().__init__()
        self.talisman = t

    @button(label="<", custom_id="talisman:unslash", disabled=True)
    async def unslash(self, ctx: Interaction, b: Button):
        self.talisman.current = max(0, self.talisman.current - 1)
        self.slash.disabled = False
        self.unslash.disabled = self.talisman.current < 1

        await ctx.response.defer()

        await ctx.followup.edit_message(
            ctx.message.id,  # type:ignore
            attachments=[self.talisman.get_image()],
            view=self,
        )

    @button(label=">", custom_id="talisman:slash")
    async def slash(self, ctx: Interaction, _):
        self.talisman.current = min(self.talisman.slashes, self.talisman.current + 1)
        self.slash.disabled = self.talisman.current == self.talisman.slashes
        self.unslash.disabled = False

        await ctx.response.defer()

        await ctx.followup.edit_message(
            ctx.message.id,  # type:ignore
            attachments=[self.talisman.get_image()],
            view=self,
        )

    @button(
        label="🔪", custom_id="talisman:setup", style=ButtonStyle.danger
    )  # <- label is bloody's suggestion
    async def delete(self, ctx: Interaction, _):
        pass


class TalismanCog(GroupCog, name="talisman"):
    def __init__(self, bot: CainClient) -> None:
        super().__init__()
        self.bot = bot

        with open("./data/talismans.yaml", "r") as f:
            _data = yaml.safe_load(f)
            self.pressure = _data["pressure"]
            self.tension = _data["tension"]
            self.talismans: List[Talisman] = [
                Talisman(**d) for d in _data["talismans"].values()
            ]

    @command(name="create")
    async def create(self, ctx: Interaction, name: str, max: int, decal: str = ""):
        if max not in range(1, 25):
            return await ctx.response.send_message(
                "Must have at least one and at most 24 slashes.", ephemeral=True
            )

        t = Talisman(name, max, decal=decal)
        await self.bot.talisman_channel.send(file=t.get_image(), view=TalismanView(t))
        self.talismans.append(t)

        await ctx.response.send_message("Talisman created", ephemeral=True)

    @command(name="setup")
    async def setup(self, ctx: Interaction):
        pass


async def setup(bot: CainClient):
    await bot.add_cog(TalismanCog(bot))
