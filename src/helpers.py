import builtins
from contextlib import contextmanager
from typing import Sequence
from discord import ButtonStyle, Embed, Interaction, Message
from discord.ui import View, button
import yaml

from src.globals import BOT_ID


def emote(name: str, d: dict):
    return f"<:{name.lower()}:{d['emoji_id']}>"


def emote_link(id) -> str:
    return f"https://cdn.discordapp.com/emojis/{id}.png"


def is_me(m: Message):
    return m.author.id == BOT_ID  # type:ignore


@contextmanager
def open_yaml(fp: str, and_write=True):
    with open(fp, "r") as f:
        data = yaml.safe_load(f)

    yield data

    if and_write:
        with open(fp, "w") as f:
            yaml.safe_dump(data, f)


class Paginator(View):
    def __init__(
        self,
        pages: Sequence[dict[str, str] | tuple[str, str]],
        url: str,
        url_as_thumb: bool,
        *,
        timeout: float | None = 180,
    ):
        super().__init__(timeout=timeout)
        self.pages = pages
        self.current = 0
        self.url = url
        self.url_as_thumb = url_as_thumb

    @property
    def content(self) -> Embed:
        e: Embed

        match self.pages[self.current]:
            case builtins.dict(p):
                e = Embed(description=f"### {p['name']}\n{p['description']}")
            case builtins.tuple(p):
                e = Embed(description="### " "\n".join(self.pages[self.current]))

        if self.url_as_thumb:
            return e.set_thumbnail(url=self.url)
        else:
            return e.set_image(url=self.url)

    @button(label="<", style=ButtonStyle.primary)
    async def prev(self, ctx: Interaction, *_):
        self.current = (self.current - 1) % len(self.pages)
        await self.update(ctx)

    @button(label=">", style=ButtonStyle.primary)
    async def next(self, ctx: Interaction, *_):
        self.current = (self.current + 1) % len(self.pages)
        await self.update(ctx)

    async def update(self, ctx: Interaction):
        await ctx.response.edit_message(embed=self.content)

    async def setup(self, ctx: Interaction, **kwargs):
        await ctx.response.send_message(embed=self.content, view=self, **kwargs)
