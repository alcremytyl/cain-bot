from enum import IntEnum, auto
from typing import Tuple

from discord import SelectOption
from discord.ui import Select


class Blasphemy(IntEnum):

    @staticmethod
    def as_select_opts() -> Select:
        return Select()
