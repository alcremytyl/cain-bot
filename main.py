from discord import Interaction, Message
from src.bot import client as cainridge
from os import environ
from ast import literal_eval

from src.cogs.talisman import TALISMAN_PATH, Talisman, TalismanEditModal, TalismanView
from src.helpers import open_yaml


@cainridge.tree.context_menu(name="set talisman")
async def set_talisman(ctx: Interaction, m: Message):
    if len(m.attachments) != 1:
        return await ctx.response.send_message("Only supports single-image talismans.")
    if not m.attachments[0].filename == "talisman.png":
        return await ctx.response.send_message("Not marked as a talisman.")
    if m.attachments[0].description is None:
        return await ctx.response.send_message("No talisman data found in description")

    # WE SMUGGLING THE DATA WITH THIS ONE 🔥🔥🔥🔥
    desc_data = literal_eval(m.attachments[0].description)

    mo = TalismanEditModal()
    await ctx.response.send_modal(mo)
    await mo.wait()

    if not str(mo.text).isdigit():
        return ctx.followup.send("Input a number, Feb.", ephemeral=True)

    n = int(str(mo.text))

    with open_yaml(TALISMAN_PATH) as data:
        t = Talisman(**desc_data, sync_to_yaml=False)

        if n in range(0, t.slashes + 1):
            data["talismans"][t.name]["current"] = int(str(mo.text))
        else:
            return await ctx.followup.send(
                f"Needs to be within 0 - {t.slashes}", ephemeral=True
            )

    view = TalismanView(t)
    await m.edit(attachments=[t.get_image()], view=view)


cainridge.run(environ["discord_token"])
