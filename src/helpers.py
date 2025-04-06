from typing import Any, List
from discord import ButtonStyle, ui, Interaction
from discord.ui import View


def emote(name: str, d: dict):
    return f"<:{name.lower()}:{d['emoji_id']}>"


def emote_link(id) -> str:
    return f"https://cdn.discordapp.com/emojis/{id}.png"


class Paginator(View):
    def __init__(self, pages: List[Any], *, timeout: float | None = 180):
        super().__init__(timeout=timeout)
        self.pages = pages
        self.current = 0

    @ui.button(label="<", style=ButtonStyle.primary)
    async def prev(self, ctx: Interaction, *_):
        self.current -= 1
        await self.update(ctx)

    @ui.button(label=">", style=ButtonStyle.primary)
    async def next(self, ctx: Interaction, *_):
        self.current += 1
        await self.update(ctx)

    async def update(self, ctx: Interaction):
        await ctx.response.edit_message(
            content=self.pages[self.current % len(self.pages)], view=self
        )
