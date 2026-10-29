"""Render Serenium Finance LinkedIn graphics (1200x627) in the "Ledger" identity.

Usage:  python3 render.py specs.json OUTPUT_DIR

specs.json is a list of objects. Common fields:
  file     output file name, e.g. "Serenium-Post-2026-11-02.png"
  layout   "concept" | "number" | "checklist" | "quote"
  kicker   small label above the title (mono, oxblood), e.g. "Concepto clave"
Layout fields:
  concept    title (the term), body (1-2 sentence plain definition)
  number     number (e.g. "7", "40%"), title (short line), body (optional source/explanation)
  checklist  title, items (3-5 short strings)
  quote      title (one strong sentence), body (optional attribution / context)
Optional: footer (defaults to "Fractional controller  ·  English / Español")
          format  "li" (default, 1200x627 LinkedIn) | "ig" (1080x1350 Instagram/Facebook feed)
"""
import json, sys, html, pathlib
from playwright.sync_api import sync_playwright

HERE = pathlib.Path(__file__).resolve().parent
FONTS = (HERE / "fonts").as_uri()

CSS = f"""
@font-face {{ font-family: 'CaslonDisplay'; src: url('{FONTS}/LibreCaslonDisplay-Regular.ttf'); }}
@font-face {{ font-family: 'CaslonText'; src: url('{FONTS}/LibreCaslonText.ttf'); font-weight: 400 700; }}
@font-face {{ font-family: 'CaslonText'; src: url('{FONTS}/LibreCaslonText-Italic.ttf'); font-style: italic; }}
@font-face {{ font-family: 'PlexMono'; src: url('{FONTS}/IBMPlexMono-Regular.ttf'); }}
* {{ box-sizing: border-box; margin: 0; padding: 0; }}
html, body {{ width: 1200px; height: 627px; }}
body {{
  background-color: #F5F3EE;
  background-image: repeating-linear-gradient(to bottom, transparent 0 32px, #E2DDD3 32px 33px);
  color: #1C1A17; font-family: 'CaslonText', Georgia, serif; position: relative; overflow: hidden;
  font-feature-settings: "liga" 1, "dlig" 0, "hlig" 0;
}}
.margin {{ position: absolute; top: 0; bottom: 0; left: 104px; width: 7px;
  border-left: 1.5px solid #C98A90; border-right: 1.5px solid #C98A90; }}
.page {{ position: absolute; left: 160px; right: 88px; top: 66px; bottom: 66px; display: flex; flex-direction: column; }}
.kicker {{ font-family: 'PlexMono', monospace; font-size: 18px; color: #7A2430; letter-spacing: .02em; }}
.content {{ flex: 1; display: flex; flex-direction: column; justify-content: center; gap: 22px; }}
.title {{ font-family: 'CaslonDisplay', Georgia, serif; font-size: 66px; line-height: 1.05; letter-spacing: -.01em; text-wrap: balance; }}
.title.long {{ font-size: 52px; }}
.body {{ font-size: 26px; line-height: 1.45; color: #3E3A35; max-width: 860px; text-wrap: pretty; }}
.dbl {{ border-bottom: 5px double #7A2430; padding-bottom: 2px; }}
.num {{ font-family: 'CaslonDisplay', Georgia, serif; font-size: 190px; line-height: .9; color: #7A2430; display: inline-block;
  border-bottom: 9px double #7A2430; padding-bottom: 6px; align-self: flex-start; }}
.row {{ display: flex; gap: 48px; align-items: center; }}
.list {{ display: grid; grid-template-columns: 56px 1fr; border-top: 2px solid #1C1A17; font-size: 27px; }}
.list span {{ padding: 13px 0; border-bottom: 1px solid #CFCAC0; }}
.list .n {{ font-family: 'PlexMono', monospace; font-size: 18px; color: #7A2430; padding-top: 18px; }}
.list span.last {{ border-bottom: 4px double #1C1A17; }}
.quote {{ font-family: 'CaslonText', Georgia, serif; font-style: italic; font-size: 50px; line-height: 1.2; color: #1C1A17; text-wrap: balance; }}
.foot {{ display: flex; justify-content: space-between; align-items: baseline; font-family: 'PlexMono', monospace; font-size: 15px; color: #5E5850; }}
.mark {{ font-family: 'CaslonDisplay', Georgia, serif; font-size: 26px; color: #1C1A17; border-bottom: 3px double #1C1A17; line-height: 1.15; }}
.body.small {{ font-size: 22px; }}
.title.listtitle {{ font-size: 44px; }}
.body.attr {{ font-size: 22px; font-family: 'PlexMono', monospace; color: #5E5850; }}
/* Instagram / Facebook feed 1080x1350 */
html.ig, html.ig body {{ width: 1080px; height: 1350px; }}
html.ig body {{ background-image: repeating-linear-gradient(to bottom, transparent 0 44px, #E2DDD3 44px 45px); }}
html.ig .margin {{ left: 84px; width: 9px; }}
html.ig .page {{ left: 140px; right: 84px; top: 110px; bottom: 100px; }}
html.ig .kicker {{ font-size: 28px; }}
html.ig .content {{ gap: 40px; }}
html.ig .title {{ font-size: 104px; line-height: 1.02; }}
html.ig .title.long {{ font-size: 84px; }}
html.ig .body {{ font-size: 38px; line-height: 1.42; max-width: none; }}
html.ig .dbl {{ border-bottom-width: 8px; }}
html.ig .row {{ flex-direction: column; align-items: flex-start; gap: 44px; }}
html.ig .num {{ font-size: 260px; border-bottom-width: 12px; }}
html.ig .list {{ grid-template-columns: 80px 1fr; font-size: 40px; }}
html.ig .list span {{ padding: 22px 0; }}
html.ig .list .n {{ font-size: 26px; padding-top: 32px; }}
html.ig .quote {{ font-size: 78px; }}
html.ig .foot {{ font-size: 22px; }}
html.ig .body.small {{ font-size: 34px; }}
html.ig .title.listtitle {{ font-size: 64px; }}
html.ig .body.attr {{ font-size: 30px; }}
html.ig .mark {{ font-size: 42px; border-bottom-width: 5px; }}
"""

def esc(s):
    return html.escape(s or "")

def build(spec):
    lay = spec.get("layout", "concept")
    title = esc(spec.get("title"))
    body = esc(spec.get("body"))
    long_cls = " long" if len(spec.get("title", "")) > 42 else ""
    if lay == "concept":
        inner = f'<p class="title{long_cls}"><span class="dbl">{title}</span></p>' + (f'<p class="body">{body}</p>' if body else "")
    elif lay == "number":
        inner = (f'<div class="row"><span class="num">{esc(spec.get("number"))}</span>'
                 f'<div style="display:flex;flex-direction:column;gap:16px">'
                 f'<p class="title long">{title}</p>' + (f'<p class="body small">{body}</p>' if body else "") + '</div></div>')
    elif lay == "checklist":
        items = spec.get("items", [])
        rows = "".join(
            f'<span class="n{" last" if i == len(items) - 1 else ""}">{i + 1:02d}</span><span class="{"last" if i == len(items) - 1 else ""}">{esc(t)}</span>'
            for i, t in enumerate(items))
        inner = f'<p class="title listtitle">{title}</p><div class="list">{rows}</div>'
    elif lay == "quote":
        inner = f'<p class="quote">{title}</p>' + (f'<p class="body attr">{body}</p>' if body else "")
    else:
        raise ValueError(f"unknown layout {lay}")
    footer = esc(spec.get("footer", "Fractional controller  ·  English / Español"))
    cls = ' class="ig"' if spec.get("format") == "ig" else ""
    return f"""<!doctype html><html{cls}><head><meta charset="utf-8"><style>{CSS}</style></head><body>
<div class="margin"></div>
<div class="page">
  <p class="kicker">{esc(spec.get("kicker"))}</p>
  <div class="content">{inner}</div>
  <div class="foot"><span class="mark">Serenium</span><span>{footer}</span></div>
</div></body></html>"""

def main():
    specs = json.loads(pathlib.Path(sys.argv[1]).read_text(encoding="utf-8"))
    out = pathlib.Path(sys.argv[2]); out.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        b = p.chromium.launch()
        pages = {}
        for s in specs:
            fmt = s.get("format", "li")
            if fmt not in pages:
                w, h = (1080, 1350) if fmt == "ig" else (1200, 627)
                pages[fmt] = b.new_page(viewport={"width": w, "height": h})
            pg = pages[fmt]
            pg.set_content(build(s), wait_until="load")
            pg.evaluate("document.fonts.ready")
            pg.wait_for_timeout(150)
            pg.screenshot(path=str(out / s["file"]))
            print("rendered", s["file"])
        b.close()

if __name__ == "__main__":
    main()
