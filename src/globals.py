from os import environ
import discord

from src.helpers import emote_link


TEST_GUILD = discord.Object(int(environ["test_guild"]))
ICON_URL = "https://cdn.discordapp.com/attachments/1112259815905951780/1353591695446380555/image.png"
CAIN_EMOTE_DATA = ("cain", 1354946062032437440)
CAIN_EMOTE = f"<:{CAIN_EMOTE_DATA[0]}:{CAIN_EMOTE_DATA[1]}>"
CACHE_SIZE = 256
CAIN_EMOTE_LINK = emote_link(CAIN_EMOTE_DATA[1])
