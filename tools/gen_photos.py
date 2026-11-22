# Генерує фото для демо-сайтів за demo/<slug>/images.json через Gemini API (безкоштовна модель Nano Banana 2 Lite).
# Ключ береться з файлу ~/.gemini-key (у репозиторії його немає). Уже наявні фото пропускає.
# usage: python tools/gen_photos.py [slug ...] [--only img/hero.webp] [--force]
import base64, io, json, os, sys, time, urllib.error, urllib.request
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
MODEL = os.environ.get('GEMINI_IMAGE_MODEL', 'gemini-3.1-flash-lite-image')
KEY = (Path.home() / '.gemini-key').read_text().strip()
URL = f'https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent'
TAIL = ' Photorealistic, natural light, shot on a full-frame camera. No text, no letters, no logos, no watermarks.'

args = [a for a in sys.argv[1:] if not a.startswith('--')]
force = '--force' in sys.argv
only = sys.argv[sys.argv.index('--only') + 1] if '--only' in sys.argv else None
if only in args:
    args.remove(only)


def generate(prompt, aspect):
    body = {'contents': [{'parts': [{'text': prompt + TAIL}]}],
            'generationConfig': {'responseModalities': ['IMAGE'], 'imageConfig': {'aspectRatio': aspect}}}
    req = urllib.request.Request(URL, data=json.dumps(body).encode(),
                                 headers={'x-goog-api-key': KEY, 'Content-Type': 'application/json'})
    for attempt in range(6):
        try:
            with urllib.request.urlopen(req, timeout=180) as r:
                d = json.load(r)
            for p in d['candidates'][0]['content']['parts']:
                if 'inlineData' in p:
                    return base64.b64decode(p['inlineData']['data'])
            raise RuntimeError('у відповіді немає картинки: ' + json.dumps(d)[:300])
        except urllib.error.HTTPError as e:
            msg = e.read().decode(errors='replace')[:400]
            if e.code == 429 or e.code >= 500:  # ліміт безкоштовного тарифу або збій: чекаємо й повторюємо
                wait = 20 * (attempt + 1)
                print(f'  {e.code}, чекаю {wait} с: {msg[:160]}', flush=True)
                time.sleep(wait)
                continue
            raise RuntimeError(f'{e.code}: {msg}')
        except (urllib.error.URLError, TimeoutError) as e:
            print('  мережа:', e, flush=True)
            time.sleep(10)
    raise RuntimeError('не вдалося після 6 спроб')


slugs = args or sorted(p.parent.name for p in (ROOT / 'demo').glob('*/images.json'))
done = failed = 0
for slug in slugs:
    for it in json.loads((ROOT / 'demo' / slug / 'images.json').read_text(encoding='utf-8')):
        if only and it['file'] != only:
            continue
        out = ROOT / 'demo' / slug / it['file']
        if out.exists() and not force:
            continue
        t = time.time()
        try:
            im = Image.open(io.BytesIO(generate(it['prompt'], it.get('aspect', '16:9')))).convert('RGB')
        except Exception as e:
            print(f'FAIL {slug}/{it["file"]}: {e}', flush=True)
            failed += 1
            continue
        w = int(it.get('width', 1600))
        if im.width > w:
            im = im.resize((w, round(im.height * w / im.width)), Image.LANCZOS)
        out.parent.mkdir(parents=True, exist_ok=True)
        im.save(out, 'WEBP', quality=80, method=6)
        done += 1
        print(f'ok {slug}/{it["file"]} {im.size} {out.stat().st_size // 1024} KB {time.time() - t:.0f} s', flush=True)
print(f'готово: {done}, помилок: {failed}')
