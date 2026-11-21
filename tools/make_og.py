# Рендерить превʼю посилань (1200×630) з шаблону tools/og.html.
# usage: python tools/make_og.py          (потрібен playwright: pip install playwright && playwright install chromium)
# Результат: media/og.jpg (СТО, головна) і media/og-<ніша>.jpg для сторінок /beauty/, /clinic/ …
import functools, http.server, threading
from pathlib import Path
from playwright.sync_api import sync_playwright
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
NICHES = ['sto', 'beauty', 'clinic', 'food', 'shop', 'fitness']

class Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a):
        pass


srv = http.server.ThreadingHTTPServer(('127.0.0.1', 0), functools.partial(Quiet, directory=str(ROOT)))
threading.Thread(target=srv.serve_forever, daemon=True).start()
base = f'http://127.0.0.1:{srv.server_address[1]}/tools/og.html'

with sync_playwright() as p:
    br = p.chromium.launch()
    page = br.new_page(viewport={'width': 1200, 'height': 630}, device_scale_factor=1)
    for n in NICHES:
        page.goto(f'{base}?n={n}')
        page.wait_for_selector('body[data-ready="1"]')
        png = ROOT / 'media' / '_og.png'
        page.screenshot(path=str(png))
        out = ROOT / 'media' / ('og.jpg' if n == 'sto' else f'og-{n}.jpg')
        Image.open(png).convert('RGB').save(out, quality=86, optimize=True, progressive=True)
        png.unlink()
        print('ok', out.name, out.stat().st_size // 1024, 'KB')
    br.close()
srv.shutdown()
