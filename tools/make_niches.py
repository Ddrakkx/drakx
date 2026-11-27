# Збирає сторінки під ніші з index.html: /beauty/, /clinic/, /food/, /shop/, /fitness/.
# Навіщо: месенджери не виконують JS, тож ?n=beauty не міняв превʼю посилання. У кожної сторінки
# свої title, description і og-картинка (media/og-<ніша>.jpg з tools/make_og.py), а тексти на сторінці
# підставляє той самий обʼєкт NICHE з index.html (через <html data-n="…">).
# usage: python tools/make_niches.py   — запускати після кожної зміни index.html
import html, re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = 'https://zentra.com.ua/'
DESC_TAIL = 'Без передоплати — спочатку показую результат.'
META = {
    'beauty': ('Сайт і Telegram-бот для запису в салон краси | Zentra', 'салонів краси та барбершопів'),
    'clinic': ('Сайт і Telegram-бот для запису в клініку | Zentra', 'клінік і кабінетів'),
    'food': ('Сайт і Telegram-бот для замовлень у кавʼярні | Zentra', 'кавʼярень і пекарень'),
    'shop': ('Сайт і Telegram-бот для замовлень у магазині | Zentra', 'магазинів'),
    'fitness': ('Сайт і Telegram-бот для запису у фітнес-студію | Zentra', 'фітнес-студій'),
}
PRO_STUDIO = [
    ('kicker', 'Вебстудія · сайти й&nbsp;Telegram&#8209;боти для&nbsp;мереж та бізнесу'),
    ('h1', 'Клієнти записуються самі&nbsp;— на&nbsp;одну точку чи цілу мережу'),
    ('hero-lead', 'Робимо сайт і&nbsp;Telegram&#8209;бот для запису на одну або кілька точок без дзвінків. Без передоплати: спочатку показуємо прототип, оплата після погодження.'),
    ('work-btn', 'Наші роботи'),
    ('services-h', 'Що ми робимо'),
    ('work-lead', 'Сайти й боти, які ми зробили для клієнтів.'),
    ('gold-aside', 'Для цього ж СТО зробили клієнтський Telegram&#8209;бот:'),
    ('volt-aside', 'До сайту додали Telegram&#8209;бот, який розподіляє заявки між майстрами за темами.'),
    ('prices-lead', 'Більшість проєктів вкладається в ці межі. Точну суму назвемо, щойно опишете завдання, і зафіксуємо письмово. Без доплат, якщо не додасте нових завдань.'),
    ('bundle-why', 'Кнопка запису на сайті веде одразу в бота, а заявки приходять вам або керівникам точок у Telegram. Робимо все за один раз, тому виходить дешевше.'),
    ('bundle-biz-cost', 'від 16&nbsp;000 до 25&nbsp;000&nbsp;грн'),
    ('bundle-biz-was', 'на 3&nbsp;000–5&nbsp;000&nbsp;грн дешевше, ніж окремо'),
    ('site-biz-cost', 'від 11&nbsp;000 до 17&nbsp;000&nbsp;грн'),
    ('bot-cab-cost', 'від 8&nbsp;000 до 13&nbsp;000&nbsp;грн'),
    ('multi-h', 'Сайт і бот для мережі з кількох філій'),
    ('multi-why', 'Одне рішення на всі адреси: клієнт обирає найближчу точку, а заявка одразу летить потрібним майстрам чи адміністратору.'),
    ('multi-p1', '<b>Додаткові точки:</b> вибір філії налаштовуємо один раз, кожна наступна адреса&nbsp;— лише +5–10%'),
    ('multi-net', '<b>Мережа 4+ точок:</b> окремий проєкт без подвійних націнок, від 21&nbsp;000&nbsp;грн'),
    ('multi-ex', 'Наприклад, сайт і бот на 4 точки&nbsp;— від 21&nbsp;000 до 31&nbsp;000&nbsp;грн'),
    ('pnote', 'Фішки, як у демо (примірка нігтів, конструктор торта чи букета), не обовʼязкові: для запису вистачає зручної форми або бота. Якщо захочете таку фішку, додамо окремо й назвемо ціну наперед.'),
    ('pcta-note', 'Відповідаємо протягом дня, у&nbsp;вихідні теж.'),
    ('how-eyebrow', 'Як ми працюємо'),
    ('how-lead', 'Так виглядає робота з нашою студією: від першого повідомлення до запуску.'),
    ('flow-name', 'Zentra Studio'),
    ('flow-sub', 'відповідаємо протягом дня'),
    ('flow-m2', 'Додали блок із цінами'),
    ('flow-m4', 'Чудово! Тоді оплата&nbsp;— і запускаємо<time>10:43</time>'),
    ('flow-bill', 'Рахунок від Zentra Studio'),
    ('flow-m5', 'Запустили! Сайт уже працює:'),
    ('term1-p', 'Перший варіант часто готовий того&nbsp;ж&nbsp;дня. Ціну, строки й склад робіт фіксуємо письмово ще до початку&nbsp;— без сюрпризів у кінці.'),
    ('term2-p', 'Розміщуємо сайт і бота та стежимо, щоб усе працювало. Перший місяць обслуговування й дрібні правки входять у ціну. Спілкуєтесь напряму з розробниками, без менеджерів: відповідаємо протягом дня.'),
    ('faq-q3', 'Перший варіант часто показуємо того&nbsp;ж&nbsp;дня, коли ви написали. Далі все залежить від кількості правок.'),
    ('faq-q4', 'Розповісти про бізнес і надіслати те, що вже є: фото, послуги, ціни, контакти. Решту робимо ми.'),
    ('faq-q6', 'На нашому хостингу: ми стежимо, щоб усе працювало. Захочете тримати все у себе&nbsp;— після оплати передамо файли й доступи.'),
    ('faq-q7', 'Файли й доступи можна забрати будь-коли після оплати: тоді сайт і бота зможе підтримувати будь-яка команда. Поки все на нашому хостингу, ми на звʼязку й відповідаємо протягом дня.'),
    ('faq-q8', 'Перший місяць входить у ціну. Далі бот коштує 350&nbsp;грн на місяць: сервер, щоб він працював цілодобово, і виправлення, якщо щось зламалось. За сайт щомісячної плати немає: лише продовження домену раз на рік, перший рік теж входить у ціну. Вартість домену залежить від зони, назвемо її заздалегідь.'),
    ('faq-q9', 'Основна робота&nbsp;— один раз налаштувати вибір філії й розподіл заявок; далі кожна нова адреса додається швидко і коштує лише +5–10%, без 20–30% за точку. Для мережі від 4 точок комплекс коштує орієнтовно від 21&nbsp;000&nbsp;грн.'),
    ('contact-lead', 'Напишіть назву бізнесу, кількість точок і що потрібно: сайт, бот чи все разом. Покажемо перший варіант безкоштовно й назвемо орієнтовну ціну.'),
    ('footer-copy', '© 2026 Zentra Studio. Усі права захищено.'),
]

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


# крихітне превʼю кожного lazy-знімка вшиваємо прямо в сторінку (style="--lq:url(data:…)", ~0,5–1,5 КБ):
# поки знімок вантажиться, під ним видно розмиту версію, а анімація «з коду» малює символи з нього, не чекаючи мережі
import base64, io
from PIL import Image
_LQ = {}


def lqip(rel):
    if rel not in _LQ:
        im = Image.open(ROOT / rel).convert('RGB')
        w = 80 if im.height < im.width * 2 else 36
        im = im.resize((w, round(im.height * w / im.width)), Image.LANCZOS)
        b = io.BytesIO()
        im.save(b, 'WEBP', quality=50, method=6)
        _LQ[rel] = 'data:image/webp;base64,' + base64.b64encode(b.getvalue()).decode()
    return _LQ[rel]


def add_lq(s):
    def f(m):
        tag = re.sub(r' style="--lq:[^"]*"', '', m[0])
        src = re.search(r' src="(media/[^"]+)"', tag)
        if not src or 'loading="lazy"' not in tag:
            return m[0]
        return tag[:-1] + f' style="--lq:url({lqip(src[1])})">'
    return re.sub(r'<img [^>]*>', f, s)


# головна теж отримує превʼю (переписуємо index.html лише якщо щось змінилось)
lq_src = add_lq(src)
if lq_src != src:
    (ROOT / 'index.html').write_text(lq_src, encoding='utf-8', newline='\n')
    src = lq_src
    print('ok index.html (lqip)')

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
        # телефон у першому екрані показує верх того самого знімка (файл спільний із карткою «Сайти»)
        s, k = re.subn(r'(<div class="hphone" id="hphone"><img) src="[^"]*" srcset="[^"]*"(.*?) height="\d+" alt="[^"]*"',
                       lambda m: f'{m[1]} src="media/demo-{d0["slug"]}-m-360.webp" srcset="' + ', '.join(f'media/demo-{d0["slug"]}-m-{w}.webp {w}w' for w in (360, 480, 720))
                       + f'"{m[2]} height="{d0["mh"]}" alt="Демо-сайт «{html.escape(d0["name"])}» на телефоні"', s, count=1)
        assert k == 1
        s = add_lq(s)
    # сторінка лежить на рівень глибше: відносні шляхи до файлів через ../
    s = re.sub(r'(?<=["(, ])(fonts/|media/|demo/|favicon\.svg|favicon-48\.png|apple-touch-icon\.png)', r'../\1', s)
    out = ROOT / n / 'index.html'
    out.parent.mkdir(exist_ok=True)
    out.write_text(s, encoding='utf-8')
    urls.append(url)
    print('ok', out.relative_to(ROOT))

# окрема статична сторінка для мереж і великого бізнесу: /pro/ (режим студії Zentra Studio)
s = src
pro_url = f'{SITE}pro/'
pro_img = f'{SITE}media/og-pro.jpg'
pro_title = 'Сайти й Telegram-боти для мереж і бізнесу | Zentra Studio'
pro_h1 = 'Клієнти записуються самі — на одну точку чи цілу мережу'
pro_desc = 'Сайти й Telegram-боти для мереж, автосервісів і бізнесу з кількома точками. Без передоплати: спочатку показуємо прототип.'
pro_ogd = 'Без передоплати: спочатку показуємо готовий прототип, оплата після погодження.'
s = s.replace('<html lang="uk">', '<html lang="uk" class="pro" data-v="pro">', 1)
s = re.sub(r'<title>[^<]*</title>', f'<title>{html.escape(pro_title)}</title>', s, count=1)
s = meta(s, 'name', 'description', pro_desc)
s = meta(s, 'property', 'og:site_name', 'Zentra Studio')
s = meta(s, 'property', 'og:title', pro_h1)
s = meta(s, 'property', 'og:description', pro_ogd)
s = meta(s, 'property', 'og:image', pro_img)
s = meta(s, 'property', 'og:image:alt', f'{pro_h1} — вебстудія Zentra Studio, без передоплати')
s = meta(s, 'property', 'og:url', pro_url)
s = meta(s, 'name', 'twitter:title', pro_h1)
s = meta(s, 'name', 'twitter:description', pro_ogd)
s = meta(s, 'name', 'twitter:image', pro_img)
s = re.sub(r'(<link rel="canonical" href=")[^"]*(")', rf'\g<1>{pro_url}\g<2>', s, count=1)
s = s.replace('"name":"Zentra"', '"name":"Zentra Studio"', 1)
s = s.replace('aria-label="Zentra, на початок"', 'aria-label="Zentra Studio, на початок"', 1)
s = s.replace('class="prices" id="prices-grid"', 'class="prices pro" id="prices-grid"', 1)
for eid, val in PRO_STUDIO:
    s, k = re.subn(rf'(<[a-z0-9]+\b[^>]*\bid="{re.escape(eid)}"[^>]*>).*?(</[a-z0-9]+>)',
                   lambda m, v=val: m[1] + v + m[2], s, count=1, flags=re.S)
    assert k == 1, eid
s = re.sub(r'(?<=["(, ])(fonts/|media/|demo/|favicon\.svg|favicon-48\.png|apple-touch-icon\.png)', r'../\1', s)
pro_out = ROOT / 'pro' / 'index.html'
pro_out.parent.mkdir(exist_ok=True)
pro_out.write_text(s, encoding='utf-8')
urls.append(pro_url)
print('ok', pro_out.relative_to(ROOT))

(ROOT / 'sitemap.xml').write_text(
    '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    + ''.join(f'  <url><loc>{u}</loc></url>\n' for u in urls) + '</urlset>\n', encoding='utf-8')
(ROOT / 'robots.txt').write_text(f'User-agent: *\nAllow: /\nSitemap: {SITE}sitemap.xml\n', encoding='utf-8')
print('ok sitemap.xml, robots.txt')
