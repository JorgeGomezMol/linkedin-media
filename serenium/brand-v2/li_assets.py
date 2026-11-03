"""Render Serenium v2 LinkedIn assets (logo + banners) in the glass style."""
import pathlib
from playwright.sync_api import sync_playwright

OUT = pathlib.Path("/home/claude/glass/linkedin"); OUT.mkdir(exist_ok=True)
MARK = ('<circle cx="32" cy="32" r="29" fill="#0C1017" stroke="#9CC3AE" stroke-width="2.4"/>'
        '<path transform="matrix(-1 0 0 1 64 0)" d="M32 3a14.5 14.5 0 0 1 0 29a14.5 14.5 0 0 0 0 29" fill="none" stroke="#F2F4F7" stroke-width="2.6" stroke-linecap="round"/>')
FONTS = '<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Libre+Caslon+Display&display=swap" rel="stylesheet">'
BASE = """*{box-sizing:border-box;margin:0;padding:0}
body{background:#0C1017;color:#F2F4F7;font-family:Inter,sans-serif;overflow:hidden;position:relative}
.m{position:absolute;border-radius:50%;filter:blur(var(--b,90px))}
.serif{font-family:'Libre Caslon Display',Georgia,serif;font-weight:400}
.k{font-weight:600;letter-spacing:.14em;text-transform:uppercase;color:#9CC3AE}"""

def html(w, h, body, extra=""):
    return f"<!doctype html><html><head><meta charset='utf-8'>{FONTS}<style>html,body{{width:{w}px;height:{h}px}}{BASE}{extra}</style></head><body>{body}</body></html>"

ASSETS = {
 # Company logo 400x400 (LinkedIn shows it square)
 "Serenium-LinkedIn-logo-400.png": (400, 400, html(400, 400, f"""
   <div class="m" style="width:300px;height:300px;left:-120px;top:-140px;background:#1F3B66;opacity:.55"></div>
   <div class="m" style="width:260px;height:260px;right:-120px;bottom:-120px;background:#2E5A4A;opacity:.5"></div>
   <svg viewBox="0 0 64 64" style="position:absolute;left:80px;top:80px;width:240px;height:240px">{MARK}</svg>""")),
 # Company page banner 1128x191 (logo overlaps lower-left on desktop; keep content right/centre)
 "Serenium-LinkedIn-banner-empresa-1128x191-v2.png": (1128, 191, html(1128, 191, f"""
   <div class="m" style="--b:70px;width:520px;height:420px;left:-120px;top:-220px;background:#1F3B66;opacity:.6"></div>
   <div class="m" style="--b:70px;width:420px;height:360px;right:-60px;top:-160px;background:#2E5A4A;opacity:.55"></div>
   <div style="position:absolute;left:300px;right:56px;top:0;bottom:0;display:flex;align-items:center;justify-content:space-between;gap:28px">
     <div><p class="serif" style="font-size:33px;line-height:1.12">Controller-level accounting<br>for a small number of clients.</p>
       <p class="k" style="font-size:11px;margin-top:12px">Bookkeeping · Accounting · Fractional controller</p></div>
     <div style="display:flex;align-items:center;gap:12px;padding:12px 18px;border-radius:16px;background:rgba(255,255,255,.07);border:1px solid rgba(255,255,255,.16)">
       <svg viewBox="0 0 64 64" style="width:38px;height:38px">{MARK}</svg>
       <div><p class="serif" style="font-size:22px;line-height:1">Serenium</p><p style="font-size:12px;color:#C3CAD4;margin-top:5px">sereniumfinance.com</p></div></div>
   </div>""")),
 # Personal profile banner 1584x396 (profile photo covers lower-left)
 "Serenium-LinkedIn-banner-perfil-1584x396-v2.png": (1584, 396, html(1584, 396, f"""
   <div class="m" style="--b:110px;width:760px;height:620px;left:-200px;top:-320px;background:#1F3B66;opacity:.6"></div>
   <div class="m" style="--b:110px;width:620px;height:560px;right:-120px;bottom:-300px;background:#2E5A4A;opacity:.55"></div>
   <div style="position:absolute;left:560px;right:90px;top:0;bottom:0;display:flex;flex-direction:column;justify-content:center">
     <p class="k" style="font-size:15px">Bookkeeping · Accounting · Fractional controller</p>
     <p class="serif" style="font-size:54px;line-height:1.08;margin-top:16px">Controller-level accounting<br>for a small number of clients.</p>
     <div style="display:flex;align-items:center;gap:14px;margin-top:26px">
       <svg viewBox="0 0 64 64" style="width:40px;height:40px">{MARK}</svg>
       <p style="font-size:17px;color:#C3CAD4"><span class="serif" style="font-size:23px;color:#F2F4F7">Serenium</span>&nbsp;&nbsp;·&nbsp;&nbsp;sereniumfinance.com</p></div>
   </div>""")),
}

with sync_playwright() as p:
    b = p.chromium.launch()
    for name, (w, h, content) in ASSETS.items():
        pg = b.new_page(viewport={"width": w, "height": h}, device_scale_factor=2)
        pg.set_content(content, wait_until="networkidle"); pg.wait_for_timeout(800)
        pg.screenshot(path=str(OUT / name)); pg.close(); print("rendered", name)
    b.close()
