from discord import Message

from src.globals import BOT_ID


def emote(name: str, d: dict):
    return f"<:{name.lower()}:{d['emoji_id']}>"


def emote_link(id) -> str:
    return f"https://cdn.discordapp.com/emojis/{id}.png"


def is_me(m: Message):
    return m.author.id == BOT_ID  # type:ignore
