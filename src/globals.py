from glob import glob
from typing import List
import discord
import yaml


with open("./data/config.yaml") as f:
    _config = yaml.safe_load(f)
with open("./data/state.yaml") as f:
    _state = yaml.safe_load(f)

CACHE_SIZE: int = _config["cache_size"]
CAIN_EMOTE: str = _config["cain_emote"]
CAIN_EMOTE_LINK: str = _config["cain_emote_link"]
OWNER_IDS: List[int] = _config["owner_ids"]
TALISMAN_CHANNEL = (int(_state["guild_id"]), int(_state["talisman"]["channel_id"]))


COG_DIR = "./src/cogs/"
COGS = [g[len(COG_DIR) : -3] for g in glob(COG_DIR + "*.py")]

TEST_GUILD = discord.Object(TALISMAN_CHANNEL[0])
