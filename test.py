from PIL import Image, ImageFont
import numpy as np

DECAL_DIMENSIONS = (110, 112)
TEXT_DIMENSIONS = (570, 112)

img = Image.open("./assets/talisman.png")
decal = Image.open("./assets/decals/wormy.png")
font = ImageFont.truetype("./assets/Apex-Black.ttf")

decal.thumbnail(DECAL_DIMENSIONS, Image.Resampling.LANCZOS)
d = decal.copy()
d.putalpha(20)

img.dra

img.paste(d, (0, 0), decal)
img.show()

decal.close()
img.close()
