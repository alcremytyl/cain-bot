from discord import Interaction
from discord.app_commands import Transform, Transformer


class OptionalFmtString(Transformer):
    async def transform(self, _: Interaction, value: str | None) -> str | None:
        if value is None:
            return None

        return value.lower().strip()


StringArg = Transform[str | None, OptionalFmtString] | None
