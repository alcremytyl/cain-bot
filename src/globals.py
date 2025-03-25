from os import environ
import tomllib
from typing import Literal, Optional
import discord

agenda_choices = (
    "Beast",
    "Doomed",
    "Firebug",
    "Guardian",
    "Loner",
    "Hardline",
    "Machine",
    "Moth",
    "Temperance",
    "Torch",
    "Departed",
    "Shadow",
    "Sorcerer",
    "Songbird",
    "Demon",
    "Survivor",
)
blasphemy_choices = (
    "Tension",
    "Ardence",
    "Flux",
    "Vector",
    "Gate",
    "Smother",
    "Whisper",
    "Edit",
    "Bind",
    "Palace",
    "Jaunt",
    "Sympathy",
)
blasphemy_abilities: dict[str, list[str]] = dict()

blasphemy_colors = (0xFF0000, 0xFFC800, 0x0974F3, 0xF600FF)

TEST_GUILD = discord.Object(int(environ["test_guild"]))
ICON_URL = "https://cdn.discordapp.com/attachments/1112259815905951780/1353591695446380555/image.png"
global data

with open("./assets/data.toml", "rb") as f:
    data = tomllib.load(f)


for name, _data in data["blasphemy"].items():
    blasphemy_abilities[name] = []

    for ability in _data["abilities"]:
        blasphemy_abilities[name].append(ability[0])
