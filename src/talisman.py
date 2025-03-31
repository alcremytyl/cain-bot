from dataclasses import dataclass, field
from glob import glob
from random import choice as rand_choice
from typing import Dict, List, Self
import csv

from PIL import Image as image, ImageDraw, ImageFont
from PIL.Image import Image
from discord import Message, ui
from discord.ui.view import View

"""
slash-left-max = 220
slash-right-max = 765

offset ~= (right - left)/capacity


increase size of talisman image by 20 vertical pad
place slashes 10px above
max rot of 15deg


also render the slash capacity
"""

TALISMAN_DIMENSIONS = (785, 112)
DECAL_DIMENSIONS = (112, 112)
DECAL_DIR = "./assets/decals/"
DECAL_CHOICES = tuple(
    map(lambda x: x[len(DECAL_DIR) : -4], glob("./assets/decals/*.png"))
)
TALISMAN_TEMPLATE_PATH = "./assets/talisman.png"
TALISMAN_FONT_PATH = "./assets/Apex-Black.ttf"
TALISMAN_DIR = "./tmp/"
FONT = ImageFont.truetype(TALISMAN_FONT_PATH, size=50)

decal_pool = set(DECAL_CHOICES) - {"execution", "pressure", "wormy"}


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
        choice = rand_choice(list(decal_pool))
        decal_pool -= {choice}
        return choice

    def slash(self, count: int = 1) -> bool:
        """If true, resolve"""
        self.count += count
        return self.current >= self.max

    def unslash(self, count: int = 1):
        self.count -= count

    def set(self, value: int):
        self.count = value

    def get_decal_fp(self) -> str:
        return f"{DECAL_DIR}{self.decal_path}.png"

    def get_image_fp(self) -> str:
        return f"{TALISMAN_DIR}{self.name}.png"

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

        img = image.open(TALISMAN_TEMPLATE_PATH)
        draw = ImageDraw.Draw(img, mode="RGBA")
        decal = image.open(f"{DECAL_DIR}{self.decal_path}.png")
        text_size = (
            TALISMAN_DIMENSIONS[0] - FONT.size / 4,
            TALISMAN_DIMENSIONS[1] - FONT.size,
        )

        decal.thumbnail(DECAL_DIMENSIONS, image.Resampling.LANCZOS)
        mask = decal.copy()
        decal.putalpha(50)
        img.paste(decal, mask)
        draw.text(text_size, self.name.upper(), (0, 0, 0, 56), FONT, "rm")
        img.save(f"./tmp/{self.name}.png", format="PNG")

        self._image = img


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


# class TalismanMenu(View):
#     def __init__(self, *_):
#         super().__init__(timeout=None)
#
#     @ui.button(label="")
