# Готує медіа для кейсів: скриншот -> webp (2 розміри).
# usage: python tools/make_media.py <screenshot.png> <name>
import sys
from pathlib import Path
from PIL import Image

src, name = sys.argv[1], sys.argv[2]
out = Path(__file__).resolve().parent.parent / 'media'
im = Image.open(src).convert('RGB')

def save(img, suffix, w, q=78):
    h = round(img.height * w / img.width)
    img.resize((w, h), Image.LANCZOS).save(out / f'{name}{suffix}-{w}.webp', 'WEBP', quality=q, method=6)

# звичайна версія
for w in (720, 1440):
    save(im, '', w)

print('ok', name, im.size)
