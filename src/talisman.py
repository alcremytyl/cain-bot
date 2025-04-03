from dataclasses import dataclass, field
from glob import glob
import random
import asyncio
from typing import Dict, List, Self, Tuple
import csv

from PIL import Image as image, ImageDraw, ImageFont
from PIL.Image import Image, Resampling
from PIL.ImageFilter import GaussianBlur
from discord import (
    ButtonStyle,
    File,
    Interaction,
    InteractionMessage,
    Message,
    TextStyle,
    ui,
)
from discord.ui.button import button, Button
from discord.ui.view import View


TALISMAN_DIMENSIONS = (785, 112)
DECAL_DIMENSIONS = (100, 100)
DECAL_OFFSET = (132, 112)
DECAL_DIR = "./assets/decals/"
DECAL_CHOICES = set([a[len(DECAL_DIR) : -4] for a in glob(f"{DECAL_DIR}*.png")])
DECAL_RESERVED = {"execution", "tension", "pressure", "resolved"}
TALISMAN_TEMPLATE_PATH = "./assets/talisman.png"
TALISMAN_FONT_PATH = "./assets/Apex-Black.ttf"
TALISMAN_DIR = "./tmp/"
SLASH_CHOICES = glob("./assets/slashes/*.png")
FONT = ImageFont.truetype(TALISMAN_FONT_PATH, size=50)
SLASH_TEXT_CENTER = (161, 54)
SLASH_TEXT_ARGS = {
    "xy": SLASH_TEXT_CENTER,
    "fill": (255, 255, 255, 255),
    "font": FONT,
    "anchor": "mm",
    "stroke_fill": (12, 6, 24, 255),
    "stroke_width": 4,
}
NAME_TEXT_ARGS = {
    "xy": (TALISMAN_DIMENSIONS[0] - FONT.size / 4, TALISMAN_DIMENSIONS[1] - FONT.size),
    "fill": (0, 0, 0, 204),
    "font": FONT,
    "anchor": "rm",
}

decal_pool = set(DECAL_CHOICES) - {"execution", "pressure", "wormy", "resolved"}


@dataclass
class Talisman:
    name: str
    current: int
    max: int
    id: int
    decal_path: str = field(default="USERANDOM")
    _image: Image = field(init=False)

    @staticmethod
    def get_random_decal() -> str:
        global decal_pool
        choice = random.choice(list(decal_pool))
        decal_pool -= {choice}
        return choice

    def slash(self, count: int = 1) -> bool:
        """If true, resolve"""
        self.current += count
        self.sync_image()
        return self.current >= self.max

    def unslash(self, count: int = 1):
        self.current = max(0, self.current - count)
        self.sync_image()

    def set(self, value: int):
        self.current = max(0, value)

    def get_decal_fp(self) -> str:
        return f"{DECAL_DIR}{self.decal_path}.png"

    def get_image(self) -> List[File]:
        fp = f"./tmp/{self.name}.png"
        self.sync_image()
        self._image.save(fp, format="PNG")
        return [File(fp, "talisman.png")]

    @staticmethod
    def centered_coords(obj: Image, x=0, y=0) -> Tuple[int, int]:
        return (
            (DECAL_OFFSET[0] - obj.width + x) // 2,
            (DECAL_OFFSET[1] - obj.height + y) // 2,
        )

    def sync_image(self):
        img = image.open(TALISMAN_TEMPLATE_PATH).convert("RGBA")

        # decal
        decal = image.open(f"{DECAL_DIR}{self.decal_path}.png")
        decal.thumbnail(DECAL_DIMENSIONS, Resampling.LANCZOS)
        img.paste(decal, Talisman.centered_coords(decal), decal)

        # slashes
        for n in range(self.current):
            slash = image.open(random.choice(SLASH_CHOICES))
            new_offset = random.randrange(-5, 5)
            size = (slash.width + (new_offset * slash.width < 20), slash.height)
            slash = (
                slash.rotate(random.randrange(-2, 10), expand=True)
                .resize(size)
                .filter(GaussianBlur((0.2, 1.5)))
            )

            img.paste(slash, Talisman.centered_coords(slash), slash)

        # text
        txt = image.new("RGBA", img.size, (255, 255, 255, 0))
        txt_draw = ImageDraw.Draw(txt)
        txt_draw.text(text=str(self.name), **NAME_TEXT_ARGS)
        txt_draw.text(text=str(self.max), **SLASH_TEXT_ARGS)
        img.paste(txt, txt)

        # resolve
        resolve = image.open(f"{DECAL_DIR}resolved.png")
        img.paste(resolve, Talisman.centered_coords(resolve), resolve)

        img.save(f"./tmp/{self.name}.png", format="PNG")
        self._image = img

    def to_dict(self) -> dict[str, str | int]:
        return {
            "name": self.name,
            "decal_path": self.decal_path,
            "current": self.current,
            "max": self.max,
            "id": self.id,
        }

    def __repr__(self) -> str:
        return f"Talisman(name={self.name}, progress=({self.current}/{self.max}))"

    def __eq__(self, value, /) -> bool:
        if isinstance(value, Talisman):
            return self.id == value.id
        return False

    def __hash__(self) -> int:
        return hash(self.id)

    def __post_init__(self):
        self.name = self.name.lower()

        if self.decal_path == "USERANDOM":
            self.decal_path = Talisman.get_random_decal()

        self.sync_image()


class TalismansManager(Dict[int, Talisman]):
    def __init__(self):
        self.messages: List[Message] = []

    def __contains__(self, key: object, /) -> bool:
        match key:
            case int(x):
                return x in self.keys()
            case str(x):
                if x.isdigit():
                    return int(x) in self.keys()
                else:
                    return False
            case _:
                return False

    @classmethod
    def load(cls) -> Self:
        t = cls()

        with open("./data/talismans.csv", "r") as f:
            data = csv.DictReader(f)

            for d in data:
                d = {
                    "name": d["name"],
                    "decal_path": d["decal_path"],
                    "current": int(d["current"]),
                    "max": int(d["max"]),
                    "id": int(d["id"]),
                }
                t.messages.append(d["id"])
                t.add(Talisman(**d))

        return t

    def update_talisman(self, new: Talisman):
        self[new.id] = new
        self.sync_csv()

    def add(self, new: Talisman) -> bool:
        """returns if already existed"""

        exists = new.id in self.keys()

        if not exists:
            print(f"[TALISMAN]: appending `{new.id}` ({ new.name })")
            self[new.id] = new
            self.sync_csv()

        return exists

    def sync_csv(self):
        """syncs csv content to TalismanManager state"""
        with open("./data/talismans.csv", "r") as f:
            read = csv.DictReader(f)
            data = [t.to_dict() for t in self.values()]
            fields = read.fieldnames

            if fields is None:
                raise ValueError("No header for Talisman CSV")

        with open("./data/talismans.csv", "w") as f:
            write = csv.DictWriter(f, fields)
            write.writeheader()
            write.writerows(data)

    # TODO:
    def reset(self):
        pass


# TODO: do that shit here breh
class TalismanModal(ui.Modal):
    def __init__(self, manager: TalismansManager) -> None:
        self.manager = manager
        super().__init__(title="Talisman Editor", timeout=180)

    value, decal, name = (
        ui.TextInput(label=label, placeholder="...", required=False)
        for label in ["Slashes", "Decal", "Name"]
    )

    #
    async def on_submit(self, interaction: Interaction, /) -> None:
        content = str()
        talisman = self.manager[interaction.message.id]  # type:ignore

        if (v := self.value.value).isdigit():
            content += f"Set talisman to {v}"
            talisman.set(int(v))
        elif len(self.value.value) > 0:
            content += f"Cannot set talisman to a non-number."

        if (v := self.decal.value.lower().strip()) in DECAL_CHOICES:
            content += f"Set decal to {v}"
            talisman.decal_path = v

        if len(v := self.name.value) > 0:
            content += f"Set name to {v}"
            talisman.name = v

        talisman.sync_image()

        await interaction.response.send_message(content=content, ephemeral=True)
        return await super().on_submit(interaction)

    async def on_error(self, interaction: Interaction, error: Exception, /) -> None:
        print(f"[ERROR] {error}")
        await interaction.response.send_message(
            "Make sure to set value to a number", ephemeral=True
        )
        return await super().on_error(interaction, error)


class TalismanMenu(View):
    def __init__(self, manager: TalismansManager):
        super().__init__(timeout=None)
        self.manager = manager

    @button(label="<", style=ButtonStyle.primary)
    async def unslash(self, ctx: Interaction, _: Button):
        if (msg := ctx.message) is None:
            await ctx.response.send_message("uh oh")
            return

        t = self.manager[msg.id]
        t.unslash()
        self.manager.sync_csv()

        await msg.edit(attachments=t.get_image())
        await ctx.response.send_message(
            f"Talisman `{t.name}` unslashed. *( {t.current} / {t.max} )*",
            ephemeral=True,
        )

    @button(label=">", style=ButtonStyle.primary)
    async def slash(self, ctx: Interaction, _: Button):
        if (msg := ctx.message) is None:
            await ctx.response.send_message("uh oh")
            return

        t = self.manager[msg.id]
        if t.slash():
            # TODO: talisman resolution logic
            await msg.channel.send("resolve that hoe")

        self.manager.sync_csv()
        await msg.edit(attachments=t.get_image())

        await ctx.response.send_message(
            f"Talisman `{t.name}` slashed. *( {t.current} / {t.max} )*", ephemeral=True
        )

    @button(label=":gear:", style=ButtonStyle.secondary)
    async def set(self, ctx: Interaction, _: Button):
        # TODO: check if admin
        if (msg := ctx.message) is None:
            await ctx.response.send_message("uh oh")
            return

        await ctx.response.send_message(view=TalismanModal(self.manager))

    @button(label=":x:", style=ButtonStyle.danger)
    async def delete(self, ctx: Interaction, *_):
        # TODO: ownre check
        pass
