def emote(name: str, d: dict):
    return f"<:{name.lower()}:{d['emoji_id']}>"


def emote_link(id) -> str:
    return f"https://cdn.discordapp.com/emojis/{id}.png"
