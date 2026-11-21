# Обрізає Inter до символів сайту й ваг 400–700 (було 67 КБ, стало ~29 КБ).
# usage: python tools/make_fonts.py <папка з повними inter-lat.woff2 та inter-cyr.woff2>
#   повні файли є в історії git:  git show b27e890:fonts/inter-lat.woff2 > src/inter-lat.woff2  (так само inter-cyr)
#   потрібно: pip install fonttools brotli
# Важливо: хінтинг (таблиці prep/gasp) НЕ викидати — без нього Chromium на Linux розсуває «т» та інші складені гліфи.
# Якщо на сайті зʼявився новий символ (₴, →, ≈ …), додай його код у LAT/CYR, запусти скрипт і онови unicode-range в index.html.
import io, sys
from pathlib import Path
from fontTools import subset
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer

SRC = Path(sys.argv[1])
OUT = Path(__file__).resolve().parent.parent / 'fonts'
LAT = list(range(0x20, 0x7f)) + [0xa0, 0xa9, 0xab, 0xb7, 0xbb, 0xd7, 0x2bc, 0x2013, 0x2014, 0x2019, 0x201c, 0x201d, 0x201e, 0x2026, 0x2212]
CYR = [0x301, 0x404, 0x406, 0x407, 0x454, 0x456, 0x457, 0x490, 0x491, 0x2116] + list(range(0x410, 0x450))
FEATURES = ['kern', 'mark', 'mkmk', 'ccmp', 'locl', 'calt', 'tnum', 'pnum']

for name, codes in [('inter-lat', LAT), ('inter-cyr', CYR)]:
    o = subset.Options()
    o.layout_features = FEATURES
    o.name_IDs = [1, 2]
    o.name_languages = [0x409]
    f = TTFont(SRC / f'{name}.woff2')
    s = subset.Subsetter(o)
    s.populate(unicodes=codes)
    s.subset(f)
    buf = io.BytesIO(); f.flavor = None; f.save(buf); buf.seek(0)
    f = instancer.instantiateVariableFont(TTFont(buf), {'wght': (400, 700)})
    if name == 'inter-lat':  # нерозривний дефіс (U+2011, «Telegram‑боти») малюємо звичайним дефісом
        for t in f['cmap'].tables:
            if t.isUnicode():
                t.cmap[0x2011] = t.cmap[0x2d]
    f.flavor = 'woff2'
    out = OUT / f'{name}.woff2'
    f.save(out)
    print('ok', out.name, out.stat().st_size // 1024, 'KB')
