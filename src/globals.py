from os import environ
import tomllib
from typing import Literal, Optional
import discord

agenda_choices = Optional[Literal['Beast','Doomed','Firebug','Guardian','Loner','Hardline','Machine','Moth','Temperance','Torch','Departed','Shadow','Sorcerer','Songbird','Demon','Survivor']]
blasphemy_choices = Optional[Literal['Tension', 'Ardence', 'Flux', 'Vector', 'Gate','Smother','Whisper','Edit','Bind','Palace','Jaunt','Sympathy']]

TEST_GUILD = discord.Object(int(environ["test_guild"]))
ICON_URL = "https://cdn.discordapp.com/attachments/1112259815905951780/1353591695446380555/image.png"
global data

with open("./assets/data.toml", "rb") as f:
    data = tomllib.load(f)


