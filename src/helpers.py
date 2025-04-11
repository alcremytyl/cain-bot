from contextlib import contextmanager
from discord import Message
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
