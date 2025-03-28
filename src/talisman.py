from dataclasses import dataclass
from typing import Tuple


@dataclass
class Talisman:
    name: str
    progress: Tuple[int, int]
