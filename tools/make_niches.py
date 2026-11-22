# Збирає сторінки під ніші з index.html: /beauty/, /clinic/, /food/, /shop/, /fitness/.
# Навіщо: месенджери не виконують JS, тож ?n=beauty не міняв превʼю посилання. У кожної сторінки
# свої title, description і og-картинка (media/og-<ніша>.jpg з tools/make_og.py), а тексти на сторінці
# підставляє той самий обʼєкт NICHE з index.html (через <html data-n="…">).
# usage: python tools/make_niches.py   — запускати після кожної зміни index.html
import html, re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = 'https://ddrakkx.github.io/drakx/'
DESC_TAIL = 'Без передоплати — спочатку показую результат.'
META = {
    'beauty': ('Сайт і Telegram-бот для запису в салон краси | drakx', 'салонів краси та барбершопів'),
    'clinic': ('Сайт і Telegram-бот для запису в клініку | drakx', 'клінік і кабінетів'),
    'food': ('Сайт і Telegram-бот для замовлень у кавʼярні | drakx', 'кавʼярень і пекарень'),
    'shop': ('Сайт і Telegram-бот для замовлень у магазині | drakx', 'магазинів'),
    'fitness': ('Сайт і Telegram-бот для запису у фітнес-студію | drakx', 'фітнес-студій'),
}

src = (ROOT / 'index.html').read_text(encoding='utf-8')
# k (надзаголовок) і h1 кожної ніші беремо з JS-обʼєкта NICHE, щоб тексти жили в одному місці
niche_js = dict((m[0], (m[1], m[2])) for m in re.findall(r"(\w+):\{k:'([^']*)',h1:'([^']*)'", src))


def plain(s):
    return html.unescape(re.sub(r'<[^>]+>', '', s)).replace(' ', ' ').replace('‑', '-')


def meta(s, attr, key, val):
    pat = rf'(<meta {attr}="{re.escape(key)}" content=")[^"]*(")'
    assert re.search(pat, s), key
    return re.sub(pat, lambda m: m[1] + html.escape(val, quote=True) + m[2], s)


# демо-сайти для ніш: tools/demos.json (назва, вид бізнесу, місто, що можна спробувати, висота мобільного знімка)
import json
DEMOS = json.loads((ROOT / 'tools' / 'demos.json').read_text(encoding='utf-8')) if (ROOT / 'tools' / 'demos.json').exists() else {}


def demo_block(items):
    e = lambda t: html.escape(t, quote=True)
    cards = ''.join(f"""
      <article class="demo-card rv"{' style="--d:.08s"' if i else ''}>
        <a class="shot" href="demo/{d['slug']}/" target="_blank" rel="noopener" tabindex="-1" aria-hidden="true"><div class="bar"><i></i><i></i><i></i><u>Демо · {e(d['name'])}</u></div>
          <div class="dview"><img src="media/demo-{d['slug']}-720.webp" srcset="media/demo-{d['slug']}-720.webp 720w, media/demo-{d['slug']}-1440.webp 1440w" sizes="(max-width:700px) 92vw, 520px" width="1440" height="900" alt="" loading="lazy" decoding="async"></div></a>
        <p class="tag">Демо · {e(d['kind'])} · {e(d['city'])}</p>
        <h3>{e(d['name'])}</h3>
        <p>{e(d['wow'])}</p>
        <a class="link" href="demo/{d['slug']}/" target="_blank" rel="noopener">Відкрити демо <span aria-hidden="true">↗</span><span class="sr"> (відкриється в новій вкладці)</span></a>
      </article>""" for i, d in enumerate(items))
    return f'<div class="demos"><div class="demo-grid">{cards}\n    </div></div>\n    <p class="eyebrow cases-h rv">Реальні клієнти: автосервіси</p>'


urls = [SITE]
for n, (title, who) in META.items():
    k, h1 = niche_js[n]
    s = src
    url = f'{SITE}{n}/'
    img = f'{SITE}media/og-{n}.jpg'
    h1p = plain(h1)
    desc = f'{h1p.replace(" — ", ", ")}: сайт і Telegram-бот для {who}. {DESC_TAIL}'
    ogd = 'Без передоплати: спочатку показую готовий сайт чи бота, оплата потім.'
    s = s.replace('<html lang="uk">', f'<html lang="uk" data-n="{n}">', 1)
    s = re.sub(r'<title>[^<]*</title>', f'<title>{html.escape(title)}</title>', s, count=1)
    s = meta(s, 'name', 'description', desc)
    s = meta(s, 'property', 'og:title', h1p)
    s = meta(s, 'property', 'og:description', ogd)
    s = meta(s, 'property', 'og:image', img)
    s = meta(s, 'property', 'og:image:alt', f'{h1p} — сайт і Telegram-бот, без передоплати')
    s = meta(s, 'property', 'og:url', url)
    s = meta(s, 'name', 'twitter:title', h1p)
    s = meta(s, 'name', 'twitter:description', ogd)
    s = meta(s, 'name', 'twitter:image', img)
    s = re.sub(r'(<link rel="canonical" href=")[^"]*(")', rf'\g<1>{url}\g<2>', s, count=1)
    # без JS теж видно свою нішу: заголовок і надзаголовок вписуємо прямо в розмітку
    s = re.sub(r'(<p class="eyebrow" id="kicker">)[^<]*(</p>)', lambda m: m[1] + k + m[2], s, count=1)
    s = re.sub(r'(<h1 id="h1">).*?(</h1>)', lambda m: m[1] + h1 + m[2], s, count=1)
    # демо для ніші: два живі сайти перед реальними кейсами, а телефон у картці «Сайти» гортає перше демо
    if DEMOS.get(n):
        s = s.replace('<!--demos-->', demo_block(DEMOS[n]), 1)
        d0 = DEMOS[n][0]
        s, k = re.subn(r'(<div class="phone" id="phone"><img) src="[^"]*" srcset="[^"]*"(.*?) height="\d+" alt="[^"]*"',
                       lambda m: f'{m[1]} src="media/demo-{d0["slug"]}-m-360.webp" srcset="' + ', '.join(f'media/demo-{d0["slug"]}-m-{w}.webp {w}w' for w in (360, 480, 720))
                       + f'"{m[2]} height="{d0["mh"]}" alt="Демо-сайт «{html.escape(d0["name"])}» на телефоні"', s, count=1)
        assert k == 1
    # сторінка лежить на рівень глибше: відносні шляхи до файлів через ../
    s = re.sub(r'(?<=["(, ])(fonts/|media/|demo/|favicon\.svg|favicon-48\.png|apple-touch-icon\.png)', r'../\1', s)
    out = ROOT / n / 'index.html'
    out.parent.mkdir(exist_ok=True)
    out.write_text(s, encoding='utf-8')
    urls.append(url)
    print('ok', out.relative_to(ROOT))

(ROOT / 'sitemap.xml').write_text(
    '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    + ''.join(f'  <url><loc>{u}</loc></url>\n' for u in urls) + '</urlset>\n', encoding='utf-8')
(ROOT / 'robots.txt').write_text(f'User-agent: *\nAllow: /\nSitemap: {SITE}sitemap.xml\n', encoding='utf-8')
print('ok sitemap.xml, robots.txt')
