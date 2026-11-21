# Готує медіа для кейсів: скриншот -> webp (2 розміри) + «рентген»-версія (каркас) для лінзи.
# usage: python tools/make_media.py <screenshot.png> <name>
import sys
from pathlib import Path
from PIL import Image, ImageFilter, ImageOps

src, name = sys.argv[1], sys.argv[2]
out = Path(__file__).resolve().parent.parent / 'media'
im = Image.open(src).convert('RGB')

def save(img, suffix, w, q=78):
    h = round(img.height * w / img.width)
    img.resize((w, h), Image.LANCZOS).save(out / f'{name}{suffix}-{w}.webp', 'WEBP', quality=q, method=6)

# звичайна версія
for w in (720, 1440):
    save(im, '', w)

# каркас: сірі контури елементів на білому (сайт монохромний, тож сірим одразу,
# без CSS-фільтра, який довелося б перераховувати на кожному кадрі руху лінзи)
g = ImageOps.grayscale(im)
e = g.filter(ImageFilter.FIND_EDGES)
e = ImageOps.autocontrast(e, cutoff=2)
e = e.point(lambda v: 0 if v < 38 else min(255, int((v - 38) * 2.2)))
e = e.filter(ImageFilter.MaxFilter(3))            # трохи товщі лінії
base = Image.new('L', im.size, 255)
ink = Image.new('L', im.size, 110)
xr = Image.composite(ink, base, e)
for w in (720, 1440):
    save(xr, '-x', w, q=72)
print('ok', name, im.size)
