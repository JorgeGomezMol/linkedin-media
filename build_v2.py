"""Build the Serenium v2 site (glass design, English only).

Usage: python3 build_v2.py OUT_DIR [LOGO]   LOGO in A|B|C|D|current (default current)
Writes index.html, services/, approach/, about/, contact/ (+ contact/send.php) and .htaccess.
"""
import sys, pathlib, re, html

OUT = pathlib.Path(sys.argv[1]); OUT.mkdir(parents=True, exist_ok=True)
LOGO = (sys.argv[2] if len(sys.argv) > 2 else "current").upper()
SAMPLE = pathlib.Path(__file__).with_name("sample.html").read_text(encoding="utf-8")
CSS = SAMPLE[SAMPLE.index("<style>") + 7: SAMPLE.index("</style>")]
PORTRAIT = pathlib.Path("/home/claude/msp-docs/portrait.txt").read_text().strip()

CAL = "https://app.onecal.io/b/jorge-gomez/jorge-gomez-lets-talk"
WA = "https://wa.me/18402746945?text=" + "Hi%20Jorge%2C%20I%20saw%20the%20Serenium%20website%20and%20would%20like%20to%20talk%20about%20my%20company%27s%20accounting."
EMAIL = "hello@sereniumfinance.com"

# ---------- logo options (64x64 viewBox) ----------
LOGOS = {
 "CURRENT": '<rect width="64" height="64" rx="15" fill="#9CC3AE"/><text x="32" y="44" font-family="\'Libre Caslon Display\', Georgia, serif" font-size="41" fill="#0C1017" text-anchor="middle">S</text><rect x="20" y="49" width="24" height="2.2" fill="#0C1017"/><rect x="20" y="53.2" width="24" height="2.2" fill="#0C1017"/>',
 "A": '<rect x="1.5" y="1.5" width="61" height="61" rx="15" fill="rgba(255,255,255,.06)" stroke="#9CC3AE" stroke-width="2"/><text x="32" y="43" font-family="\'Libre Caslon Display\', Georgia, serif" font-size="38" fill="#F2F4F7" text-anchor="middle">S</text><rect x="21" y="48.5" width="22" height="2" fill="#9CC3AE"/><rect x="21" y="52.5" width="22" height="2" fill="#9CC3AE"/>',
 "B": '<circle cx="32" cy="32" r="30" fill="none" stroke="#9CC3AE" stroke-width="1.6"/><circle cx="32" cy="32" r="24.5" fill="none" stroke="rgba(242,244,247,.35)" stroke-width="1"/><text x="32" y="42" font-family="\'Libre Caslon Display\', Georgia, serif" font-size="30" fill="#F2F4F7" text-anchor="middle">S</text><rect x="24" y="45" width="16" height="1.6" fill="#9CC3AE"/><rect x="24" y="48.2" width="16" height="1.6" fill="#9CC3AE"/>',
 "C": '<rect width="64" height="64" rx="15" fill="#9CC3AE"/><rect x="15" y="34" width="7" height="16" rx="1.5" fill="#0C1017"/><rect x="28.5" y="24" width="7" height="26" rx="1.5" fill="#0C1017"/><rect x="42" y="14" width="7" height="36" rx="1.5" fill="#0C1017" opacity=".55"/><rect x="13" y="53" width="38" height="1.8" fill="#0C1017"/><rect x="13" y="56.4" width="38" height="1.8" fill="#0C1017"/>',
 "Y1": '<circle cx="32" cy="32" r="30" fill="#F2F4F7"/><path transform="matrix(-1 0 0 1 64 0)" d="M32 2a30 30 0 0 1 0 60a15 15 0 0 1 0-30a15 15 0 0 0 0-30z" fill="#9CC3AE"/><circle cx="32" cy="32" r="30" fill="none" stroke="#9CC3AE" stroke-width="2"/>',
 "Y2": '<circle cx="32" cy="32" r="29" fill="rgba(255,255,255,.05)" stroke="#9CC3AE" stroke-width="2.4"/><path transform="matrix(-1 0 0 1 64 0)" d="M32 3a14.5 14.5 0 0 1 0 29a14.5 14.5 0 0 0 0 29" fill="none" stroke="#F2F4F7" stroke-width="2.6" stroke-linecap="round"/>',
 "Y3": '<circle cx="32" cy="32" r="30" fill="#141A23"/><path transform="matrix(-1 0 0 1 64 0)" d="M32 2a30 30 0 0 1 0 60a15 15 0 0 1 0-30a15 15 0 0 0 0-30z" fill="#9CC3AE"/><circle cx="32" cy="17" r="4.2" fill="#9CC3AE"/><circle cx="32" cy="47" r="4.2" fill="#141A23"/><circle cx="32" cy="32" r="30" fill="none" stroke="#9CC3AE" stroke-width="2"/>',
}
MARK = LOGOS.get(LOGO, LOGOS["CURRENT"]) if LOGO != "D" else None
# favicon: use the mark itself when it's a symbol logo
if MARK and LOGO.startswith("Y"):
    _fav = MARK.replace('fill="rgba(255,255,255,.05)"', 'fill="#0C1017"')
    _svg = "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'>" + _fav.replace('"', "'") + "</svg>"
    FAVICON_OVERRIDE = "data:image/svg+xml," + _svg.replace("#", "%23").replace("<", "%3C").replace(">", "%3E").replace("'", "%27").replace(" ", "%20")
else:
    FAVICON_OVERRIDE = None
FAV_BG = {"A": "#0C1017", "B": "#0C1017", "D": "#0C1017"}.get(LOGO, "#9CC3AE")
FAV_INK = "#0C1017" if FAV_BG == "#9CC3AE" else "#9CC3AE"
FAVICON = ("data:image/svg+xml," + (
    f"<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'><rect width='64' height='64' rx='14' fill='{FAV_BG}'/>"
    f"<text x='32' y='44' font-family='Georgia,serif' font-size='40' fill='{'#0C1017' if FAV_BG=='#9CC3AE' else '#F2F4F7'}' text-anchor='middle'>S</text>"
    f"<rect x='20' y='49' width='24' height='2' fill='{FAV_INK}'/><rect x='20' y='53' width='24' height='2' fill='{FAV_INK}'/></svg>"
).replace("#", "%23").replace("<", "%3C").replace(">", "%3E").replace("'", "%27").replace(" ", "%20"))

if FAVICON_OVERRIDE: FAVICON = FAVICON_OVERRIDE

EXTRA = """
.brand b .dot{color:var(--accent)}
.page-hero{padding:104px 0 56px}
.page-hero h1{font-size:clamp(38px,5vw,60px);max-width:860px}
.page-hero .lead{max-width:680px}
.cols{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:18px}
.cols2{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:18px}
.box{background:var(--surface-2);border:1px solid var(--line);border-radius:var(--radius);padding:26px;min-width:0}
.box h3{font-size:18px;font-weight:600;margin:0 0 8px;line-height:1.35}
.box p{color:var(--text-2);font-size:15.5px;margin:0}
.box .n{display:block;font-family:var(--serif);font-size:30px;color:var(--accent);line-height:1;margin-bottom:14px}
.compare{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:18px}
.compare .box h3{display:flex;align-items:center;gap:10px}
.compare ul,.incl{list-style:none;padding:0;margin:14px 0 0}
.compare li,.incl li{position:relative;padding:9px 0 9px 26px;border-top:1px solid var(--line);color:var(--text-2);font-size:15.5px}
.compare li::before,.incl li::before{content:"";position:absolute;left:2px;top:19px;width:12px;height:2px;background:var(--muted)}
.compare .us li::before,.incl li::before{background:var(--accent)}
.compare .us{border-color:rgba(156,195,174,.45)}
.band{background:var(--surface-2);border-top:1px solid var(--line);border-bottom:1px solid var(--line);padding:56px 0}
.band .wrap{display:flex;flex-wrap:wrap;align-items:center;justify-content:space-between;gap:20px 40px}
.band p{font-family:var(--serif);font-size:clamp(24px,3vw,34px);line-height:1.25;margin:0;max-width:760px}
.timeline{list-style:none;padding:0;margin:0;border-left:2px solid var(--line)}
.timeline li{position:relative;padding:0 0 30px 32px}
.timeline li::before{content:"";position:absolute;left:-7px;top:8px;width:12px;height:12px;border-radius:50%;background:var(--bg);border:2px solid var(--accent)}
.timeline .d{font-size:13px;font-weight:600;letter-spacing:.1em;text-transform:uppercase;color:var(--accent)}
.timeline h3{font-size:19px;font-weight:600;margin:4px 0 6px}
.timeline p{color:var(--text-2);margin:0;font-size:15.5px}
.split{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:56px;align-items:start}
.offer{display:grid;grid-template-columns:minmax(0,1.1fr) minmax(0,1fr);gap:40px;padding:36px;margin-bottom:22px;background:var(--surface-2);border:1px solid var(--line);border-radius:var(--radius)}
.offer.lead-offer{border-color:rgba(156,195,174,.45)}
.offer h2{font-size:clamp(28px,3vw,36px)}
.offer .price{margin:10px 0 18px}
.offer p{color:var(--text-2);margin:0 0 12px}
.about-grid{display:grid;grid-template-columns:minmax(0,360px) minmax(0,1fr);gap:56px;align-items:start}
.portrait img{width:100%;height:auto;aspect-ratio:1/1;object-fit:cover;border-radius:var(--radius);border:1px solid var(--line);display:block}
.prose p{color:var(--text-2);margin:0 0 16px}
.prose p.big{font-family:var(--serif);font-size:clamp(24px,2.6vw,30px);line-height:1.3;color:var(--text)}
.chips{display:flex;flex-wrap:wrap;gap:10px;margin-top:20px}
.chips span{font-size:13px;font-weight:500;padding:7px 12px;border-radius:999px;border:1px solid var(--line);color:var(--text-2);background:var(--surface-2)}
.quote{padding:30px 32px}
.quote p{font-family:var(--serif);font-size:clamp(22px,2.4vw,28px);line-height:1.3;margin:0}
.quote span{display:block;margin-top:14px;font-size:14px;color:var(--text-2)}
.faq details{border-top:1px solid var(--line);padding:18px 0}
.faq details:last-child{border-bottom:1px solid var(--line)}
.faq summary{cursor:pointer;font-weight:600;font-size:17px;list-style:none;display:flex;justify-content:space-between;gap:16px}
.faq summary::-webkit-details-marker{display:none}
.faq summary::after{content:"+";color:var(--accent);font-size:22px;line-height:1}
.faq details[open] summary::after{content:"–"}
.faq p{color:var(--text-2);margin:12px 0 0;max-width:820px}
form.contact-form{display:grid;gap:14px}
.field label{display:block;font-size:14px;font-weight:600;margin-bottom:6px}
.field input,.field select,.field textarea{width:100%;font:inherit;font-size:16px;color:var(--text);background:var(--bg);border:1px solid rgba(255,255,255,.22);border-radius:12px;padding:12px 14px}
.field textarea{min-height:120px;resize:vertical}
.field input:focus,.field select:focus,.field textarea:focus{outline:2px solid var(--accent);outline-offset:1px;border-color:transparent}
.hp{position:absolute;left:-9999px;width:1px;height:1px;overflow:hidden}
.form-box{background:var(--surface);border:1px solid var(--line);border-radius:var(--radius);padding:28px}
.formmsg{border-radius:12px;padding:14px 16px;margin-bottom:16px;font-size:15px;display:none}
.formmsg.ok{display:block;background:rgba(156,195,174,.16);border:1px solid rgba(156,195,174,.5)}
.formmsg.err{display:block;background:rgba(220,120,120,.14);border:1px solid rgba(220,120,120,.5)}
footer .grid{display:grid;grid-template-columns:minmax(0,1.4fr) repeat(2,minmax(0,1fr));gap:32px;margin-bottom:28px}
footer h4{color:var(--text);font-size:14px;margin:0 0 10px}
footer ul{list-style:none;margin:0;padding:0}
footer li{margin:6px 0}
footer a{text-decoration:none;color:var(--text-2)}
footer a:hover{color:var(--text)}
footer .legal{border-top:1px solid var(--line);padding-top:20px;line-height:1.6}
.links a[aria-current="page"]{color:var(--text)}
@media (max-width:900px){.cols,.cols2,.compare,.split,.offer,.about-grid{grid-template-columns:minmax(0,1fr)}.page-hero{padding:72px 0 40px}.offer{padding:26px;gap:18px}.about-grid{gap:32px}.portrait{max-width:340px}footer .grid{grid-template-columns:minmax(0,1fr)}}
"""

ICONS = SAMPLE[SAMPLE.index('<symbol id="i-cal"'): SAMPLE.index("</svg>", SAMPLE.index('<symbol id="i-mail"'))]


def brand():
    if MARK is None:
        return ('<a class="brand" href="/" aria-label="Serenium, Bookkeeping &amp; Accounting, home">'
                '<span class="name"><b>Serenium<span class="dot">.</span></b><small>Bookkeeping &amp; Accounting</small></span></a>')
    return ('<a class="brand" href="/" aria-label="Serenium, Bookkeeping &amp; Accounting, home">'
            '<svg class="mark" viewBox="0 0 64 64" aria-hidden="true">' + MARK + '</svg>'
            '<span class="name"><b>Serenium</b><small>Bookkeeping &amp; Accounting</small></span></a>')


def page(path, title, desc, body, active=""):
    nav = [("/services/", "Services"), ("/approach/", "Approach"), ("/about/", "About"), ("/contact/", "Contact")]
    links = "".join(f'<a class="hide-m" href="{h}"{" aria-current=\"page\"" if h==active else ""}>{t}</a>' for h, t in nav)
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:type" content="website">
<meta property="og:url" content="https://sereniumfinance.com{path}">
<link rel="canonical" href="https://sereniumfinance.com{path}">
<link rel="icon" href="{FAVICON}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Libre+Caslon+Display&display=swap" rel="stylesheet">
<style>{CSS}{EXTRA}</style>
</head>
<body>
<div class="mesh" aria-hidden="true"><i class="a"></i><i class="b"></i><i class="c"></i></div>
<svg width="0" height="0" style="position:absolute" aria-hidden="true">{ICONS}</svg>
<header>
  <div class="nav glass">
    {brand()}
    <nav class="links" aria-label="Main">
      {links}
      <a class="btn primary nav-cta" href="/contact/?topic=assessment"><span class="l">Request an Assessment</span><span class="s">Contact</span></a>
    </nav>
  </div>
</header>
<main>
{body}
</main>
<footer>
  <div class="wrap">
    <div class="grid">
      <div>{brand()}<p style="margin:14px 0 0;max-width:380px">Controller-level bookkeeping and accounting for a small number of U.S. businesses.</p></div>
      <div><h4>Practice</h4><ul><li><a href="/services/">Services &amp; pricing</a></li><li><a href="/approach/">Approach</a></li><li><a href="/about/">About</a></li></ul></div>
      <div><h4>Contact</h4><ul><li><a href="{CAL}" target="_blank" rel="noopener">Book a 30-minute call</a></li><li><a href="{WA}" target="_blank" rel="noopener">WhatsApp +1 (840) 274-6945</a></li><li><a href="mailto:{EMAIL}">{EMAIL}</a></li></ul></div>
    </div>
    <p class="legal">Serenium Finance is a trade name of Serenium Management Group LLC, a U.S.-registered (Wyoming) company. All services are delivered remotely. Serenium is not a CPA firm and does not provide audit, attest or income tax return services. QuickBooks, Xero and ConnectWise are trademarks of their respective owners; Serenium is not affiliated with or endorsed by them. © <span id="yr">2026</span> Serenium Management Group LLC.</p>
  </div>
</footer>
<a class="wa-float" href="{WA}" target="_blank" rel="noopener" aria-label="WhatsApp +1 (840) 274-6945"><svg aria-hidden="true"><use href="#i-wa"/></svg><span>WhatsApp</span></a>
<script>document.getElementById('yr').textContent=new Date().getFullYear();</script>
</body>
</html>
"""


PLANS = """
<div class="plans">
  <article class="plan">
    <span class="tag">Start here</span>
    <h3>Financial Operations Assessment</h3>
    <div class="price"><span class="amt">$1,500–$2,500</span><span class="unit">one time · fixed price</span></div>
    <p>Ten days. What's wrong in your books, quantified, with the root cause of each finding.</p>
    <p class="fit">No obligation to continue.</p>
  </article>
  <article class="plan">
    <span class="tag-space" aria-hidden="true">Start here</span>
    <h3>Monthly Close &amp; Reporting</h3>
    <div class="price"><span class="amt">$2,000–$3,500</span><span class="unit">per month</span></div>
    <p>Month-end close, bank and system reconciliations, AP/AR and a monthly reporting package.</p>
    <p class="fit">For businesses from $1M to $4M.</p>
  </article>
  <article class="plan">
    <span class="tag-space" aria-hidden="true">Start here</span>
    <h3>Fractional Controller</h3>
    <div class="price"><span class="amt">$4,400–$6,500</span><span class="unit">per month</span></div>
    <p>Everything in Monthly Close, plus margins, budget and cash forecast, internal controls and a monthly owner meeting.</p>
    <p class="fit">For businesses from $4M to $15M.</p>
  </article>
  <article class="plan">
    <span class="tag-space" aria-hidden="true">Start here</span>
    <h3>Cleanup &amp; Implementation</h3>
    <div class="price"><span class="amt">$4,000–$15,000</span><span class="unit">per project · fixed quote</span></div>
    <p>Historical cleanup, integration re-mapping, process documentation and system migrations.</p>
    <p class="fit">Usually follows an Assessment.</p>
  </article>
</div>"""

CONTACT_BLOCK = f"""
<section class="contact">
  <div class="wrap contact-grid">
    <div>
      <p class="kicker">Contact</p>
      <h2>Let's look at your numbers.</h2>
      <p class="sub" style="margin-bottom:0">Start with a 30-minute call. We'll talk about your business, your books and whether an Assessment makes sense. No preparation needed.</p>
    </div>
    <div class="ways">
      <a class="way primary" href="{CAL}" target="_blank" rel="noopener"><svg aria-hidden="true"><use href="#i-cal"/></svg><span><b>Book a 30-minute call</b><span>Pick a time on my calendar · U.S. Eastern</span></span></a>
      <a class="way" href="{WA}" target="_blank" rel="noopener"><svg aria-hidden="true"><use href="#i-wa"/></svg><span><b>WhatsApp or text</b><span>+1 (840) 274-6945</span></span></a>
      <a class="way" href="mailto:{EMAIL}"><svg aria-hidden="true"><use href="#i-mail"/></svg><span><b>Email</b><span>{EMAIL}</span></span></a>
    </div>
  </div>
</section>"""

# ================= HOME =================
home = f"""
<section class="hero">
  <div class="wrap hero-grid">
    <div>
      <p class="kicker">Bookkeeping · Accounting · Fractional controller</p>
      <h1>Controller-level accounting for a small number of clients.</h1>
      <p class="lead">A deliberately small practice for U.S. businesses from $1M to $15M. Clean books, closed on schedule, and numbers you can act on, without the cost of a full-time controller.</p>
      <div class="cta">
        <a class="btn primary" href="/contact/?topic=assessment">Request a Financial Operations Assessment</a>
        <a class="btn ghost" href="/services/">See services and pricing</a>
      </div>
    </div>
    <div class="card glass">
      <p class="q">Most bookkeepers tell you what happened. We tell you whether to believe it.</p>
      <div class="facts">
        <div><b>8–10</b><span>client accounts, total. That is the whole model.</span></div>
        <div><b>8+ yrs</b><span>controller-level work for U.S. companies</span></div>
        <div><b>10 days</b><span>for a fixed-price assessment of your books</span></div>
        <div><b>Remote</b><span>U.S.-registered, U.S. Eastern hours</span></div>
      </div>
    </div>
  </div>
</section>

<section class="solid">
  <div class="wrap">
    <p class="kicker">The difference</p>
    <h2>A bookkeeper records the past. A controller tells you if you can trust it.</h2>
    <p class="sub">We don't compete with bookkeepers. We compete with the idea of hiring a full-time controller.</p>
    <div class="compare">
      <div class="box"><h3>Typical bookkeeping</h3><ul>
        <li>Transactions categorized when there's time</li><li>The close happens "when it's done"</li><li>Reports sent without explanation</li><li>Integrations trusted, never checked</li><li>Problems surface at tax time</li></ul></div>
      <div class="box us"><h3>Serenium</h3><ul>
        <li>Every account reconciled, every month</li><li>The close happens on a fixed date</li><li>Variances explained in a conversation</li><li>Operating systems tied out to the ledger</li><li>Problems surface the month they happen</li></ul></div>
    </div>
  </div>
</section>

<section class="solid" style="border-top:0;padding-top:0">
  <div class="wrap">
    <p class="kicker">Services</p>
    <h2>Four ways to work together.</h2>
    <p class="sub">Fixed prices and monthly packages, scoped in writing. No hourly billing, and nothing below $2,000 a month.</p>
    {PLANS}
    <p class="note">Monthly engagements have a 6-month minimum. <a href="/services/">See what each one includes →</a></p>
  </div>
</section>

<div class="band"><div class="wrap">
  <p>A deliberately small practice. Your books are not one of two hundred.</p>
  <a class="btn ghost" href="/approach/">How we work</a>
</div></div>

<section class="solid" style="border-top:0">
  <div class="wrap split">
    <div>
      <p class="kicker">Who we work with</p>
      <h2>Any industry. One standard.</h2>
      <p class="sub">The level is the specialty, not the industry. We work where we already have real experience.</p>
      <div class="chips"><span>IT services &amp; MSPs</span><span>E-commerce &amp; retail</span><span>Law firms</span><span>Professional services</span><span>Construction &amp; real estate</span><span>Hospitality &amp; restaurants</span></div>
    </div>
    <div class="box">
      <h3>You'll probably recognize one of these</h3>
      <ul class="incl">
        <li>Your month-end close takes weeks, or never quite happens</li>
        <li>You don't fully trust the numbers your bookkeeper sends</li>
        <li>You're preparing to sell, borrow or bring in a partner</li>
        <li>A new system left your data in a mess</li>
        <li>Something didn't add up and nobody can explain how</li>
        <li>You've outgrown the bookkeeper you started with</li>
      </ul>
    </div>
  </div>
</section>
{CONTACT_BLOCK}
"""

# ================= SERVICES =================
def offer(tag, name, amt, unit, desc, fit, items, lead=False):
    t = f'<span class="tag" style="font-size:11px;font-weight:600;letter-spacing:.08em;text-transform:uppercase;color:var(--accent-ink);background:var(--accent);padding:4px 10px;border-radius:999px;display:inline-block;margin-bottom:14px">{tag}</span>' if tag else ""
    lis = "".join(f"<li>{i}</li>" for i in items)
    return f"""<article class="offer{' lead-offer' if lead else ''}">
  <div>{t}<h2>{name}</h2><div class="price"><span class="amt">{amt}</span><span class="unit">{unit}</span></div><p>{desc}</p><p style="color:var(--muted);font-size:14px">{fit}</p></div>
  <div><h3 style="font-size:15px;font-weight:600;margin:0;color:var(--text)">What's included</h3><ul class="incl">{lis}</ul></div>
</article>"""

services = f"""
<section class="page-hero">
  <div class="wrap">
    <p class="kicker">Services &amp; pricing</p>
    <h1>Fixed prices. Scope in writing. No hourly surprises.</h1>
    <p class="lead">Every engagement starts the same way: a fixed-price Assessment that shows you where your books stand. From there, you decide whether to continue.</p>
  </div>
</section>
<section class="solid">
  <div class="wrap">
    {offer("Start here", "Financial Operations Assessment", "$1,500–$2,500", "one time · fixed price, quoted before we start",
      "A 10-day diagnostic of the real state of your books: reconciliations, the close process, and how your operating systems feed the ledger. You get a written report of what's wrong, quantified, with the root cause of each finding.",
      "No obligation to continue. Sold on judgment, not software.",
      ["Every balance sheet account and its reconciliation, checked one by one", "Close process: what happens, when, and by whom", "Integration check between your operating systems and the ledger", "Findings quantified in dollars, with root causes", "A prioritized fix plan and a walkthrough call"], lead=True)}
    {offer("", "Monthly Close &amp; Reporting", "$2,000–$3,500", "per month · 6-month minimum",
      "The monthly accounting function, done properly and on schedule.",
      "For businesses from $1M to $4M in revenue.",
      ["Month-end close on a fixed date", "Bank, card, loan and system reconciliations", "Accounts payable and receivable", "Monthly P&amp;L, balance sheet and cash flow", "Year-end package for your CPA"])}
    {offer("", "Fractional Controller", "$4,400–$6,500", "per month · 6-month minimum",
      "The controller you'd hire if you were big enough to justify one full time.",
      "For businesses from $4M to $15M in revenue. The main offer.",
      ["Everything in Monthly Close &amp; Reporting", "Margins by client and by service line", "Budget and cash flow forecast", "Internal controls design", "Reconciled KPIs", "A monthly meeting with the owner"])}
    {offer("", "Cleanup &amp; Implementation", "$4,000–$15,000", "per project · fixed quote",
      "For books that need rebuilding before they can be maintained. Usually follows an Assessment.",
      "Scoped and priced after the Assessment.",
      ["Historical cleanup and catch-up", "Re-mapping integrations into the ledger", "Process documentation and SOPs", "System migrations, e.g. desktop to cloud"])}
  </div>
</section>
<section class="solid" style="border-top:0;padding-top:0">
  <div class="wrap">
    <p class="kicker">How pricing works</p>
    <h2>A few rules, stated up front.</h2>
    <div class="cols" style="margin-top:32px">
      <div class="box"><h3>No hourly billing</h3><p>Monthly packages or fixed project prices. You know the number before we start.</p></div>
      <div class="box"><h3>Nothing below $2,000 a month</h3><p>We take on 8 to 10 accounts in total. Every spot goes to a client who needs controller-level work.</p></div>
      <div class="box"><h3>6-month minimum</h3><p>A clean close takes a few cycles to settle. Six months is enough to prove it works.</p></div>
    </div>
    <p class="note">We don't prepare income tax returns or perform audits. We work alongside your CPA or tax preparer and hand them clean, reconciled books.</p>
  </div>
</section>
{CONTACT_BLOCK}
"""

# ================= APPROACH =================
approach = f"""
<section class="page-hero">
  <div class="wrap">
    <p class="kicker">Approach</p>
    <h1>What happens every month, and on which day.</h1>
    <p class="lead">A controller is only as good as the routine behind the numbers. Here is ours.</p>
  </div>
</section>
<section class="solid">
  <div class="wrap split">
    <div>
      <p class="kicker">A typical close</p>
      <h2>The month, closed on a fixed date.</h2>
      <p class="sub">The calendar below is a typical Fractional Controller month. Exact dates are agreed in writing at the start.</p>
      <div class="quote glass" style="margin-top:8px"><p>Eight years inside ConnectWise taught me that most reporting problems are integration problems. Whatever system runs your business, the question is the same: does it agree with your ledger?</p><span>Jorge Gomez, founder</span></div>
    </div>
    <ol class="timeline">
      <li><span class="d">Days 1–2</span><h3>Activity in</h3><p>Bank, card, payroll and payment-processor activity captured and categorized.</p></li>
      <li><span class="d">Days 3–4</span><h3>Everything reconciled</h3><p>Every balance sheet account reconciled, and your operating systems tied out to the ledger.</p></li>
      <li><span class="d">Day 5</span><h3>Closing entries</h3><p>Accruals, prepaids, deferred revenue and depreciation booked and documented.</p></li>
      <li><span class="d">Day 6</span><h3>Controller check</h3><p>Variances investigated and explained. Anything that doesn't make sense gets an answer, not a footnote.</p></li>
      <li><span class="d">Day 7</span><h3>Package and conversation</h3><p>Financial statements and KPIs delivered, then walked through with you.</p></li>
    </ol>
  </div>
</section>
<section class="solid" style="border-top:0;padding-top:0">
  <div class="wrap">
    <p class="kicker">What you receive</p>
    <h2>Every month, the same package.</h2>
    <div class="cols" style="margin-top:32px">
      <div class="box"><span class="n">01</span><h3>Financial statements</h3><p>P&amp;L, balance sheet and cash flow, compared with last month and last year.</p></div>
      <div class="box"><span class="n">02</span><h3>Reconciliation summary</h3><p>Every account, its balance, and proof that it ties out.</p></div>
      <div class="box"><span class="n">03</span><h3>Variance notes</h3><p>What changed, why, and whether it needs your attention.</p></div>
      <div class="box"><span class="n">04</span><h3>KPIs that reconcile</h3><p>Margins, cash runway and the metrics you actually run the business on.</p></div>
      <div class="box"><span class="n">05</span><h3>Open items list</h3><p>What's pending, who owns it, and when it will be resolved.</p></div>
      <div class="box"><span class="n">06</span><h3>A real conversation</h3><p>A monthly meeting with the owner, not just an email with attachments.</p></div>
    </div>
  </div>
</section>
<section class="solid" style="border-top:0;padding-top:0">
  <div class="wrap split">
    <div>
      <p class="kicker">Getting started</p>
      <h2>From first call to first close.</h2>
      <ol class="timeline" style="margin-top:28px">
        <li><span class="d">Step 1</span><h3>30-minute call</h3><p>Your business, your systems and what's not working.</p></li>
        <li><span class="d">Step 2</span><h3>Assessment · 10 days</h3><p>A fixed-price diagnostic with written, quantified findings.</p></li>
        <li><span class="d">Step 3</span><h3>Onboarding</h3><p>Secure access, a clean chart of accounts and opening balances that tie.</p></li>
        <li><span class="d">Step 4</span><h3>First close</h3><p>The routine starts, on the date agreed in writing.</p></li>
      </ol>
    </div>
    <div class="box">
      <h3>Access and security</h3>
      <ul class="incl">
        <li>Accountant-level users with two-factor authentication, never your password</li>
        <li>We can prepare payments; you approve and release them</li>
        <li>Work happens inside your systems, not in spreadsheets on our side</li>
        <li>Fully remote, on U.S. Eastern hours</li>
      </ul>
      <h3 style="margin-top:26px">Systems we work in</h3>
      <p>QuickBooks Online and Xero for accounting, plus the operating systems that feed them: PSAs like ConnectWise, e-commerce platforms, payment processors and payroll.</p>
    </div>
  </div>
</section>
{CONTACT_BLOCK}
"""

# ================= ABOUT =================
about = f"""
<section class="page-hero">
  <div class="wrap about-grid">
    <div class="portrait"><img src="{PORTRAIT}" alt="Jorge Gomez, founder of Serenium" width="400" height="400"></div>
    <div class="prose">
      <p class="kicker">About</p>
      <h1 style="font-size:clamp(38px,5vw,58px)">Jorge Gomez</h1>
      <p style="color:var(--accent);font-weight:600;margin-top:10px">Founder · Fractional Controller</p>
      <p class="big">Fourteen years in accounting, more than eight of them at controller level for U.S. companies.</p>
      <p>I've run the full accounting function for U.S. businesses remotely: from the first transaction to the financial statements the owner signs off on. I've led accounting teams of up to five people, built SOPs and onboarding from scratch, and worked closely with several CPA firms.</p>
      <p>Today I'm also Financial Controller at an IT managed services company. That's where most of my eight years of hands-on ConnectWise come from, and why I treat every reporting problem as a possible integration problem.</p>
    </div>
  </div>
</section>
<section class="solid">
  <div class="wrap">
    <p class="kicker">What I bring</p>
    <h2>Experience you can check.</h2>
    <div class="cols" style="margin-top:32px">
      <div class="box"><h3>Controller-level accounting</h3><p>Month-end close, reconciliations, management reporting, AP and AR processes built from zero.</p></div>
      <div class="box"><h3>Systems and integrations</h3><p>About eight years in ConnectWise PSA, and experience rebuilding books that don't tie to the systems feeding them.</p></div>
      <div class="box"><h3>Fraud prevention</h3><p>Three years focused on accounting and financial fraud prevention, framed around the CFE domains.</p></div>
      <div class="box"><h3>Multi-entity and international</h3><p>International client payments, multi-country contracts, client trust accounts and retainers, cross-border flows.</p></div>
      <div class="box"><h3>Teams and process</h3><p>Accounting teams of up to five people plus agents in Latin America, with documented SOPs and onboarding.</p></div>
      <div class="box"><h3>Bilingual</h3><p>English and Spanish. Useful if your business has operations or a team in Latin America.</p></div>
    </div>
  </div>
</section>
<section class="solid" style="border-top:0;padding-top:0">
  <div class="wrap split">
    <div>
      <p class="kicker">Education</p>
      <h2>Still learning, on purpose.</h2>
      <p class="sub" style="margin-bottom:20px">Admitted to the <strong style="color:var(--text)">MS in Accounting &amp; Data Analytics at Michigan State University</strong>, starting January 2027 (in progress). Preparing for the CMA and CFE certifications.</p>
      <div class="chips"><span>MSADA · Michigan State (in progress)</span><span>QuickBooks ProAdvisor</span><span>IMA Professional Member</span><span>ACFE Associate Member</span></div>
    </div>
    <div class="box">
      <h3>Straight answers</h3>
      <ul class="incl">
        <li><b style="color:var(--text)">Not a CPA.</b> Serenium doesn't do audits or tax returns. We work alongside your CPA.</li>
        <li><b style="color:var(--text)">Fully remote.</b> Serenium Management Group LLC is registered in Wyoming. There is no U.S. office, and we won't pretend otherwise.</li>
        <li><b style="color:var(--text)">Small on purpose.</b> 8 to 10 client accounts in total, so each one gets real attention.</li>
      </ul>
    </div>
  </div>
</section>
{CONTACT_BLOCK}
"""

# ================= CONTACT =================
contact = f"""
<section class="page-hero">
  <div class="wrap">
    <p class="kicker">Contact</p>
    <h1>Let's look at your numbers.</h1>
    <p class="lead">The fastest way is a 30-minute call. You can also send a short note and we'll reply within one business day.</p>
  </div>
</section>
<section class="solid">
  <div class="wrap contact-grid">
    <div class="ways">
      <a class="way primary" href="{CAL}" target="_blank" rel="noopener"><svg aria-hidden="true"><use href="#i-cal"/></svg><span><b>Book a 30-minute call</b><span>Pick a time on my calendar · U.S. Eastern</span></span></a>
      <a class="way" href="{WA}" target="_blank" rel="noopener"><svg aria-hidden="true"><use href="#i-wa"/></svg><span><b>WhatsApp or text</b><span>+1 (840) 274-6945</span></span></a>
      <a class="way" href="mailto:{EMAIL}"><svg aria-hidden="true"><use href="#i-mail"/></svg><span><b>Email</b><span>{EMAIL}</span></span></a>
      <p class="note" style="margin-top:10px">Monday to Friday, 9 a.m. to 5 p.m. U.S. Eastern.</p>
    </div>
    <div class="form-box">
      <div id="formmsg" class="formmsg" role="status"></div>
      <form class="contact-form" method="post" action="/contact/send.php">
        <div class="field"><label for="name">Name</label><input id="name" name="name" autocomplete="name" required maxlength="120"></div>
        <div class="field"><label for="email">Email</label><input id="email" name="email" type="email" autocomplete="email" required maxlength="160"></div>
        <div class="field"><label for="company">Company and approximate annual revenue</label><input id="company" name="company" maxlength="200" placeholder="e.g. Acme Services, about $3M"></div>
        <div class="field"><label for="topic">I'm interested in</label>
          <select id="topic" name="topic">
            <option value="assessment">Financial Operations Assessment</option>
            <option value="monthly">Monthly Close &amp; Reporting</option>
            <option value="controller">Fractional Controller</option>
            <option value="cleanup">Cleanup &amp; Implementation</option>
            <option value="other">Not sure yet</option>
          </select></div>
        <div class="field"><label for="message">What's going on with your books?</label><textarea id="message" name="message" maxlength="3000"></textarea></div>
        <div class="hp" aria-hidden="true"><label for="website">Leave this empty</label><input id="website" name="website" tabindex="-1" autocomplete="off"></div>
        <button class="btn primary" type="submit" style="border:0;cursor:pointer;font:inherit;font-weight:600">Send</button>
      </form>
    </div>
  </div>
</section>
<script>
(function(){{var q=new URLSearchParams(location.search),t=q.get('topic'),s=q.get('sent'),m=document.getElementById('formmsg');
if(t){{var o=document.querySelector('#topic option[value="'+t+'"]');if(o)o.selected=true;}}
if(s==='1'){{m.className='formmsg ok';m.textContent='Thanks. Your message was sent; we\\'ll reply within one business day.';}}
if(s==='0'){{m.className='formmsg err';m.textContent='Something went wrong. Please email {EMAIL} or use WhatsApp.';}}}})();
</script>
"""

SEND_PHP = r"""<?php
// Simple contact handler for sereniumfinance.com/contact/
$to = 'hello@sereniumfinance.com';
if ($_SERVER['REQUEST_METHOD'] !== 'POST') { header('Location: /contact/'); exit; }
if (!empty($_POST['website'])) { header('Location: /contact/?sent=1'); exit; } // honeypot
function clean($v, $max) { $v = trim(strip_tags((string)$v)); $v = str_replace(["\r", "\n"], ' ', $v); return mb_substr($v, 0, $max); }
$name    = clean($_POST['name'] ?? '', 120);
$email   = filter_var(trim($_POST['email'] ?? ''), FILTER_VALIDATE_EMAIL);
$company = clean($_POST['company'] ?? '', 200);
$topic   = clean($_POST['topic'] ?? '', 40);
$message = mb_substr(trim(strip_tags((string)($_POST['message'] ?? ''))), 0, 3000);
if ($name === '' || !$email) { header('Location: /contact/?sent=0'); exit; }
$body = "Name: $name\nEmail: $email\nCompany: $company\nInterested in: $topic\n\n$message\n";
$headers = "From: Serenium website <$to>\r\nReply-To: $email\r\nContent-Type: text/plain; charset=UTF-8\r\n";
$ok = mail($to, "Website inquiry: $name", $body, $headers);
header('Location: /contact/?sent=' . ($ok ? '1' : '0'));
exit;
"""

HTACCESS = """# Serenium v2: old URLs
Redirect 301 /for-msps /approach/
Redirect 301 /drift-report /services/
Redirect 301 /preview-v2 /
"""

pages = {
    "index.html": page("/", "Serenium · Controller-level bookkeeping & accounting", "A deliberately small practice giving U.S. businesses from $1M to $15M controller-level bookkeeping and accounting: clean books, closed on schedule.", home),
    "services/index.html": page("/services/", "Services & pricing · Serenium", "Financial Operations Assessment, Monthly Close & Reporting, Fractional Controller and Cleanup & Implementation, with published prices.", services, "/services/"),
    "approach/index.html": page("/approach/", "Approach · Serenium", "How Serenium closes the month: a fixed-date close, every account reconciled, and the same package every month.", approach, "/approach/"),
    "about/index.html": page("/about/", "About Jorge Gomez · Serenium", "Jorge Gomez: 14 years in accounting, 8+ at controller level for U.S. companies, fraud prevention and systems integration experience.", about, "/about/"),
    "contact/index.html": page("/contact/", "Contact · Serenium", "Book a 30-minute call, send a WhatsApp or email Serenium.", contact, "/contact/"),
}
for rel, content in pages.items():
    p = OUT / rel; p.parent.mkdir(parents=True, exist_ok=True); p.write_text(content, encoding="utf-8")
(OUT / "contact" / "send.php").write_text(SEND_PHP, encoding="utf-8")
(OUT / ".htaccess").write_text(HTACCESS, encoding="utf-8")
print("built", LOGO, [str(OUT / k) for k in pages])
