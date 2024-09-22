from PIL import Image

img = Image.open('world.png')
img2 = Image.new('RGBA', img.size, 'WHITE')
img2.paste(img, (0, 0), img)

open('world-1ch.binp', 'wb').write(img2.convert('L').tobytes())
open('world-3ch.binp', 'wb').write(img2.convert('RGB').tobytes())
open('world-4ch.binp', 'wb').write(img.tobytes())
