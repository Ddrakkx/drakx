# Рендерить превʼю посилань (1200×630) з шаблону tools/og.html.
# usage: python tools/make_og.py          (playwright або локальний Chrome/Chromium + pillow)
# Результат: media/og.jpg (СТО, головна), media/og-pro.jpg (/pro/) і media/og-<ніша>.jpg
import functools, http.server, shutil, subprocess, threading
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
NICHES = ['sto', 'beauty', 'clinic', 'food', 'shop', 'fitness', 'pro']

class Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a):
        pass


def find_chrome():
    for c in [
        Path.home() / 'AppData/Local/ms-playwright/chromium-1228/chrome-win64/chrome.exe',
        Path(r'C:\Program Files\Google\Chrome\Application\chrome.exe'),
        Path(r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe'),
    ]:
        if c.exists():
            return str(c)
    for name in ('google-chrome', 'chromium', 'chromium-browser', 'chrome', 'msedge'):
        w = shutil.which(name)
        if w:
            return w
    raise RuntimeError('Neither playwright nor Chrome/Chromium found')


srv = http.server.ThreadingHTTPServer(('127.0.0.1', 0), functools.partial(Quiet, directory=str(ROOT)))
threading.Thread(target=srv.serve_forever, daemon=True).start()
base = f'http://127.0.0.1:{srv.server_address[1]}/tools/og.html'

try:
    from playwright.sync_api import sync_playwright
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
except ImportError:
    chrome = find_chrome()
    for n in NICHES:
        png = ROOT / 'media' / '_og.png'
        subprocess.run([
            chrome, '--headless=new', '--disable-gpu', '--virtual-time-budget=2000',
            f'--screenshot={png}', '--window-size=1200,630', f'{base}?n={n}'
        ], check=True)
        out = ROOT / 'media' / ('og.jpg' if n == 'sto' else f'og-{n}.jpg')
        Image.open(png).convert('RGB').save(out, quality=86, optimize=True, progressive=True)
        png.unlink()
        print('ok', out.name, out.stat().st_size // 1024, 'KB')
srv.shutdown()
