"""Regenerate preview/{light,dark,16px}.png: python3 scripts/preview.py
Needs a Chromium/Chrome binary (set CHROME=/path, or a Playwright chromium is auto-found)."""
import glob, json, os, subprocess, sys, tempfile
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
THEMES = {'light': dict(bg='#F9FAFC', ink='#11141C', muted='#586074', rule='#D7DCE7'),
          'dark': dict(bg='#0E1117', ink='#EEF1F7', muted='#9AA3B8', rule='#2A3040')}
GROUPS = ['navigation', 'files', 'deploy', 'site-ops', 'status', 'system', 'actions']
COLS, W, PAD = 12, 1296, 24  # px

def page(theme, size):
    t = THEMES[theme]; icons = json.load(open(os.path.join(ROOT, 'icons.json')))
    h = f'<h1>CloudGround icons — {len(icons)} @ {size}px</h1>'
    for g in GROUPS:
        h += f'<h2>{g}</h2><div class="g">'
        for i in icons:
            if i['group'] == g:
                h += (f'<div class="i"><svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
                      f'stroke-width="1.75" stroke-linecap="square" stroke-linejoin="miter">{i["svg_inner"]}</svg><span>{i["name"]}</span></div>')
        h += '</div>'
    return f'''<!doctype html><meta charset=utf-8><style>
body{{margin:0;padding:{PAD}px;width:{W-2*PAD}px;background:{t['bg']};color:{t['ink']};font:10px "IBM Plex Mono",ui-monospace,Menlo,monospace}}
h1{{font:600 14px "IBM Plex Sans",-apple-system,Helvetica,sans-serif;margin:0 0 22px}}
h2{{font-size:10px;font-weight:400;letter-spacing:.08em;text-transform:uppercase;color:{t['muted']};margin:18px 0 6px;padding-bottom:6px;border-bottom:1px solid {t['rule']}}}
.g{{display:grid;grid-template-columns:repeat({COLS},1fr)}}
.i{{display:flex;flex-direction:column;align-items:center;gap:8px;padding:6px 0;height:{52 if size>16 else 44}px}}
.i span{{font-size:10px;color:{t['muted']};white-space:nowrap}}
</style>{h}'''

def chrome():
    if os.environ.get('CHROME'): return os.environ['CHROME']
    c = glob.glob(os.path.expanduser('~/Library/Caches/ms-playwright/chromium-*/chrome-mac*/Google Chrome for Testing.app/Contents/MacOS/Google Chrome for Testing')) + \
        glob.glob(os.path.expanduser('~/.cache/ms-playwright/chromium-*/chrome-linux/chrome')) + \
        ['/Applications/Google Chrome.app/Contents/MacOS/Google Chrome']
    return sorted(c)[-1]

for name, theme, size in [('light', 'light', 24), ('dark', 'dark', 24), ('16px', 'light', 16)]:
    with tempfile.NamedTemporaryFile('w', suffix='.html', delete=False) as f: f.write(page(theme, size))
    subprocess.run([chrome(), '--headless=new', '--no-sandbox', '--hide-scrollbars', '--force-device-scale-factor=1', f'--window-size={W},{1254 if size > 16 else 1142}',
                    f'--screenshot={ROOT}/preview/{name}.png', 'file://' + f.name], stderr=subprocess.DEVNULL, timeout=60)
    os.unlink(f.name)
