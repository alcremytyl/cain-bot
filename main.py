from src.bot import client as cainridge
from os import environ


cainridge.run(environ["discord_token"])
