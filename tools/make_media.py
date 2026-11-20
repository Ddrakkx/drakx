# Готує медіа для кейсів: скриншот -> webp (2 розміри) + «рентген»-версія (каркас) для лінзи.
# usage: python tools/make_media.py <screenshot.png> <name>
import sys
from pathlib import Path
from PIL import Image, ImageFilter, ImageOps, ImageChops, ImageDraw

src, name = sys.argv[1], sys.argv[2]
out = Path(__file__).resolve().parent.parent / 'media'
im = Image.open(src).convert('RGB')

def save(img, suffix, w, q=78):
    h = round(img.height * w / img.width)
    img.resize((w, h), Image.LANCZOS).save(out / f'{name}{suffix}-{w}.webp', 'WEBP', quality=q, method=6)

# звичайна версія
for w in (720, 1440):
    save(im, '', w)

# каркас: контури елементів синім по світлій сітці
g = ImageOps.grayscale(im)
e = g.filter(ImageFilter.FIND_EDGES)
e = ImageOps.autocontrast(e, cutoff=2)
e = e.point(lambda v: 0 if v < 38 else min(255, int((v - 38) * 2.2)))
e = e.filter(ImageFilter.MaxFilter(3))            # трохи товщі лінії
base = Image.new('RGB', im.size, (238, 244, 255))
d = ImageDraw.Draw(base)
step = 24
for x in range(0, im.width, step):
    d.line([(x, 0), (x, im.height)], fill=(222, 233, 252))
for y in range(0, im.height, step):
    d.line([(0, y), (im.width, y)], fill=(222, 233, 252))
blue = Image.new('RGB', im.size, (10, 132, 255))
xr = Image.composite(blue, base, e)
for w in (720, 1440):
    save(xr, '-x', w, q=72)
print('ok', name, im.size)
