#!/usr/bin/env python3
"""Build index.html for the family trip site from trips.json (+ photos.json if present).
Run: python3 build.py   (no dependencies beyond the standard library)
"""
import json, html, os, pathlib
HERE = pathlib.Path(__file__).parent
data = json.load(open(HERE / 'trips.json', encoding='utf-8'))
photos = json.load(open(HERE / 'photos.json', encoding='utf-8')) if (HERE / 'photos.json').exists() else {}
E = lambda s: html.escape(str(s), quote=True)
money = lambda n: '$' + format(int(n), ',')

ACCENT = {'pr': '#0f7c8c', 'ami': '#d9772f', 'pc': '#3b5b8f', 'avl': '#3f7a4d', 'lp': '#7a4a8c', 'mt': '#b03a2e'}

def photo_block(key, which):
    ph = photos.get(key, [])
    if not ph: return None
    return ph[0] if which == 'hero' else ph[1:5]

def credit(p):
    return f"{E(p.get('subject',''))}. Photo: {E(p.get('author',''))}, {E(p.get('license',''))}" + (f" (<a href=\"{E(p['page_url'])}\" rel=\"noopener\">source</a>)" if p.get('page_url') else '')

def section(t):
    key = t['key']; acc = ACCENT.get(key, '#444')
    hero = photo_block(key, 'hero'); gallery = photo_block(key, 'gallery') or []
    hero_html = (f'<div class="hero" style="background-image:linear-gradient(rgba(0,0,0,.15),rgba(0,0,0,.55)),url(\'{E(hero["local"])}\')">' if hero else f'<div class="hero hero-plain" style="background:{acc}">') + \
        f'<div class="hero-text"><span class="tag">{E(t["tag"])}</span><h2>{E(t["name"])}</h2><p>{E(t["place"])}</p></div></div>'
    hero_credit = f'<p class="credit">{credit(hero)}</p>' if hero else ''
    why = ''.join(f'<li>{E(x)}</li>' for x in t['why']); catch = ''.join(f'<li>{E(x)}</li>' for x in t['catch'])
    notes = ''
    for n in t.get('notes', []):
        notes += f'<div class="note"><h4>{E(n["title"])}</h4>' + ''.join(f'<p>{E(x)}</p>' for x in n['paragraphs']) + '</div>'
    gal = ''
    if gallery:
        gal = '<div class="gallery">' + ''.join(f'<figure><img loading="lazy" src="{E(p["local"])}" alt="{E(p.get("subject",""))}"><figcaption>{credit(p)}</figcaption></figure>' for p in gallery) + '</div>'
    gt = ''.join(f'<tr><th>{E(g["from"])}</th><td>{E(g["how"])}' + (f' <a href="{E(g["link"])}" rel="noopener">Link</a>' if g.get('link') else '') + f'</td><td class="num">{E(g["est"])}</td></tr>' for g in t['getting_there'])
    houses = ''.join(f'<div class="card"><h4><a href="{E(h["url"])}" rel="noopener">{E(h["name"])}</a></h4><p>{E(h["detail"])}</p><p class="price">{E(h["price"])}</p><p class="verdict">{E(h["verdict"])}</p></div>' for h in t['houses'])
    ag = ''.join(f'<tr><th>{E(a["day"])}</th><td data-label="Everyone">{E(a["all"])}</td><td data-label="Adventure crew">{E(a["crew"])}</td><td data-label="Relaxed crew and kids">{E(a["relax"])}</td></tr>' for a in t['agenda'])
    low = sum(p['low'] for p in t['pricing']); high = sum(p['high'] for p in t['pricing'])
    pr = ''.join(f'<tr><td>{E(p["item"])}</td><td class="num">{money(p["low"])}</td><td class="num">{money(p["high"])}</td><td class="note">{E(p["note"])}</td></tr>' for p in t['pricing'])
    pr += f'<tr class="total"><td>Total for ten</td><td class="num">{money(low)}</td><td class="num">{money(high)}</td><td class="note">About {money(low/10)} to {money(high/10)} a head, kids included</td></tr>'
    links = ''.join(f'<div><h4>{E(g)}</h4><ul>' + ''.join(f'<li><a href="{E(l["url"])}" rel="noopener">{E(l["label"])}</a></li>' for l in ls) + '</ul></div>' for g, ls in t['links'].items())
    markers = ''.join(f'<li><span class="dot {E(m["kind"])}"></span>{E(m["name"])}</li>' for m in t['markers'])
    return f'''
<section id="{key}" class="trip" style="--acc:{acc}">
  {hero_html}{hero_credit}
  <div class="wrap">
    <p class="pitch">{E(t['pitch'])}</p>
    <div class="two">
      <div><h3>Why it works</h3><ul>{why}</ul></div>
      <div><h3>The catch</h3><ul>{catch}</ul></div>
    </div>
    <p class="weather"><strong>Weather that week.</strong> {E(t['weather'])}</p>
    {notes}
    {gal}
    <h3>The map</h3>
    <div class="mapwrap"><div id="map-{key}" class="map"></div><ul class="legend">{markers}</ul></div>
    <h3>Getting there</h3>
    <table class="plain"><tbody>{gt}</tbody></table>
    <h3>Where we would stay</h3>
    <div class="cards">{houses}</div>
    <h3>The week</h3>
    <div class="scroll"><table class="agenda"><thead><tr><th>Day</th><th>Everyone</th><th>Adventure crew</th><th>Relaxed crew and kids</th></tr></thead><tbody>{ag}</tbody></table></div>
    <h3>Preliminary pricing</h3>
    <div class="scroll"><table class="pricing"><thead><tr><th>Line</th><th class="num">Low</th><th class="num">High</th><th>Basis</th></tr></thead><tbody>{pr}</tbody></table></div>
    <h3>Links</h3>
    <div class="links">{links}</div>
  </div>
</section>'''

s = data['site']
cards = ''
for t in data['trips']:
    low = sum(p['low'] for p in t['pricing']); high = sum(p['high'] for p in t['pricing'])
    hero = photo_block(t['key'], 'hero')
    img = f'<img src="{E(hero["local"])}" alt="{E(t["name"])}">' if hero else f'<div class="ph" style="background:{ACCENT[t["key"]]}"></div>'
    cards += f'<a class="ocard" href="#{t["key"]}" style="--acc:{ACCENT[t["key"]]}">{img}<div class="ocard-body"><span class="tag">{E(t["tag"])}</span><h3>{E(t["name"])}</h3><p class="small">{E(t["place"])}</p><p>{E(t["pitch"].split(". ")[0])}.</p><p class="band">{money(low)} to {money(high)} for ten</p></div></a>'
rules = ''.join(f'<li>{E(r)}</li>' for r in s['rules'])
nav = ''.join(f'<a href="#{t["key"]}">{E(t["name"])}</a>' for t in data['trips'])
mapdata = json.dumps({'origins': s['origins'], 'trips': [{'key': t['key'], 'name': t['name'], 'lat': t['lat'], 'lng': t['lng'], 'zoom': t['zoom'], 'markers': t['markers'], 'acc': ACCENT[t['key']]} for t in data['trips']]})
credits = ''
for t in data['trips']:
    for p in photos.get(t['key'], []):
        credits += f'<li>{credit(p)}</li>'

page = f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex, nofollow">
<title>{E(s['title'])}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,500;9..144,700&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.css">
<style>
:root{{--bg:#faf7f2;--ink:#1f1d1a;--muted:#6b665e;--line:#e6e0d6;--card:#ffffff;--acc:#0f7c8c}}
*{{box-sizing:border-box}}
body{{margin:0;background:var(--bg);color:var(--ink);font:16px/1.55 Inter,system-ui,-apple-system,Segoe UI,sans-serif}}
h1,h2,h3,h4{{font-family:Fraunces,Georgia,serif;font-weight:700;line-height:1.15;margin:0 0 .4em}}
h1{{font-size:clamp(2rem,5vw,3.4rem)}} h2{{font-size:clamp(1.8rem,4vw,2.8rem)}} h3{{font-size:1.35rem;margin-top:1.8em;color:var(--acc)}} h4{{font-size:1.05rem}}
a{{color:var(--acc)}}
.wrap{{max-width:1080px;margin:0 auto;padding:0 16px}}
header.top{{padding:40px 16px 20px;text-align:center}}
header.top p{{max-width:760px;margin:.4em auto;color:var(--muted)}}
.disc{{background:#fff4d6;border:1px solid #f0d58a;border-radius:10px;padding:12px 16px;max-width:900px;margin:18px auto 0;font-size:.95rem}}
nav.tabs{{position:sticky;top:0;z-index:50;background:rgba(250,247,242,.96);backdrop-filter:blur(6px);border-bottom:1px solid var(--line);display:flex;gap:4px;justify-content:center;flex-wrap:wrap;padding:8px}}
nav.tabs a{{text-decoration:none;color:var(--ink);padding:8px 14px;border-radius:999px;font-weight:500}}
nav.tabs a:hover{{background:#eee7db}}
.ocards{{display:grid;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));gap:16px;margin:24px 0}}
.ocard{{display:block;background:var(--card);border:1px solid var(--line);border-radius:14px;overflow:hidden;text-decoration:none;color:var(--ink);box-shadow:0 1px 2px rgba(0,0,0,.04)}}
.ocard img,.ocard .ph{{width:100%;height:150px;object-fit:cover;display:block}}
.ocard-body{{padding:14px 16px 18px}} .ocard h3{{margin:.2em 0 .1em;color:var(--acc)}} .ocard p{{margin:.3em 0;font-size:.93rem}} .ocard .band{{font-weight:600}}
.tag{{display:inline-block;font-size:.72rem;letter-spacing:.08em;text-transform:uppercase;background:var(--acc);color:#fff;padding:3px 8px;border-radius:999px}}
.small{{color:var(--muted)}}
.two{{display:grid;grid-template-columns:1fr 1fr;gap:24px}} @media(max-width:720px){{.two{{grid-template-columns:1fr}}}}
.two ul{{padding-left:1.1em}} .two li{{margin:.35em 0}}
section.trip{{margin-top:48px;border-top:1px solid var(--line)}}
.hero{{height:min(62vh,520px);background-size:cover;background-position:center;display:flex;align-items:flex-end;color:#fff}}
.hero-plain{{height:260px}}
.hero-text{{padding:28px 16px;max-width:1080px;margin:0 auto;width:100%}} .hero-text h2{{margin:.2em 0 0;text-shadow:0 2px 12px rgba(0,0,0,.4)}} .hero-text p{{margin:.2em 0 0;font-size:1.1rem;opacity:.95}}
.credit{{font-size:.75rem;color:var(--muted);text-align:right;margin:4px 16px 0}}
.pitch{{font-size:1.15rem;margin:20px 0 10px}}
.weather{{background:#fff;border:1px solid var(--line);border-radius:10px;padding:10px 14px;font-size:.95rem}}
.note{{background:#fff;border:1px solid var(--line);border-left:4px solid var(--acc);border-radius:10px;padding:12px 16px;margin:14px 0;font-size:.95rem}} .note h4{{margin:0 0 .3em;color:var(--acc)}} .note p{{margin:.4em 0}}
.gallery{{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:12px;margin:18px 0}}
.gallery figure{{margin:0}} .gallery img{{width:100%;height:190px;object-fit:cover;border-radius:10px;display:block}} .gallery figcaption{{font-size:.72rem;color:var(--muted);margin-top:4px}}
.mapwrap{{display:grid;grid-template-columns:2fr 1fr;gap:16px}} @media(max-width:720px){{.mapwrap{{grid-template-columns:1fr}}}}
.map{{height:420px;border-radius:12px;border:1px solid var(--line);background:#e9e4da}}
.legend{{list-style:none;padding:0;margin:0;font-size:.9rem;columns:1}} .legend li{{margin:.3em 0;display:flex;gap:8px;align-items:flex-start}}
.dot{{width:12px;height:12px;border-radius:50%;flex:none;margin-top:5px;background:#999;border:2px solid #fff;box-shadow:0 0 0 1px #999}}
.dot.house{{background:var(--acc);box-shadow:0 0 0 1px var(--acc)}} .dot.airport{{background:#444;box-shadow:0 0 0 1px #444}} .dot.town{{background:#c9a227;box-shadow:0 0 0 1px #c9a227}} .dot.spot{{background:#e05a4e;box-shadow:0 0 0 1px #e05a4e}}
table{{border-collapse:collapse;width:100%;background:#fff;border:1px solid var(--line);border-radius:10px;overflow:hidden}}
th,td{{text-align:left;vertical-align:top;padding:10px 12px;border-top:1px solid var(--line);font-size:.95rem}}
thead th{{background:#f1ece3;border-top:none;font-weight:600}} tbody th{{font-weight:600;white-space:nowrap;background:#fbf9f5}}
.num{{text-align:right;white-space:nowrap}} .note{{color:var(--muted);font-size:.88rem}} tr.total td{{font-weight:700;background:#f1ece3}}
.scroll{{overflow-x:auto}} .agenda th:first-child{{width:110px}}
@media(max-width:720px){{.agenda thead{{display:none}} .agenda tr{{display:block;border-top:2px solid var(--line);padding:6px 0}} .agenda th,.agenda td{{display:block;border:none;padding:4px 12px;white-space:normal}} .agenda tbody th{{background:none;font-size:1rem;color:var(--acc)}} .agenda td:empty{{display:none}} .agenda td::before{{content:attr(data-label);display:block;font-size:.75rem;letter-spacing:.04em;text-transform:uppercase;color:var(--muted)}} .pricing{{min-width:560px}}}}
.cards{{display:grid;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));gap:14px}}
.card{{background:#fff;border:1px solid var(--line);border-radius:12px;padding:14px 16px}} .card p{{margin:.4em 0;font-size:.93rem}} .card .price{{font-weight:600}} .card .verdict{{color:var(--muted)}}
.links{{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:16px}} .links ul{{padding-left:1.1em;margin:.3em 0}} .links li{{margin:.3em 0;font-size:.95rem}}
footer{{margin:60px 0 40px;color:var(--muted);font-size:.85rem}} footer ul{{padding-left:1.1em}}
#map-overview{{height:460px}}
.party{{background:#fff;border:1px solid var(--line);border-radius:12px;padding:16px 20px;margin:20px 0}} .party ul{{padding-left:1.1em;margin:.4em 0}} .party li{{margin:.35em 0}}
</style>
</head>
<body>
<header class="top">
  <h1>{E(s['title'])}</h1>
  <p>{E(s['subtitle'])}</p>
  <p class="disc">{E(s['disclaimer'])}</p>
</header>
<nav class="tabs"><a href="#overview">Overview</a>{nav}</nav>
<main>
<section id="overview" class="wrap">
  <h3>The four options</h3>
  <div class="ocards">{cards}</div>
  <h3>Where they are from home</h3>
  <div id="map-overview" class="map"></div>
  <p class="small">Dashed lines run from Norfolk; Richmond and Austin fly their own routings. Click a pin for the name.</p>
  <div class="party"><h4>Who is going</h4><p>{E(s['party'])}</p><h4>What every option has to do</h4><ul>{rules}</ul></div>
  <p class="small">How to read the prices: each line is a low and a high for all ten people for the week, built from published rates where they exist and estimates everywhere else. The one-line total is the sum of the lines. Houses have not been quoted for these dates yet, and that line is the swing factor everywhere.</p>
</section>
{''.join(section(t) for t in data['trips'])}
</main>
<footer class="wrap">
  <p>Built {E(s['built'])} from the family trip research. Preliminary throughout. Prices are estimates for ten at holiday-week rates unless marked published. Maps: OpenStreetMap contributors. Photos as credited below.</p>
  <ul>{credits}</ul>
</footer>
<script src="https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.js"></script>
<script>
const DATA = {mapdata};
const COLORS = {{house: null, airport: '#444', town: '#c9a227', spot: '#e05a4e'}};
function tiles(map){{ L.tileLayer('https://tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{maxZoom: 18, attribution: '&copy; OpenStreetMap contributors'}}).addTo(map); }}
function pin(latlng, color, label, map, big){{ L.circleMarker(latlng, {{radius: big?9:7, color:'#fff', weight:2, fillColor: color, fillOpacity: .95}}).addTo(map).bindPopup(label); }}
// maps: initialise after full load so containers have their real size, then re-fit once more
function build(){{
  const m = L.map('map-overview', {{scrollWheelZoom:false}}); tiles(m);
  const pts = [];
  DATA.origins.forEach(o => {{ pin([o.lat,o.lng], '#444', o.name + ' (' + o.seats + ' seats)', m); pts.push([o.lat,o.lng]); }});
  const vb = DATA.origins[0];
  DATA.trips.forEach(t => {{ pin([t.lat,t.lng], t.acc, '<b>'+t.name+'</b>', m, true); pts.push([t.lat,t.lng]); L.polyline([[vb.lat,vb.lng],[t.lat,t.lng]], {{color:t.acc, weight:2, dashArray:'6 6', opacity:.8}}).addTo(m); }});
  const fitO = () => {{ m.invalidateSize(); m.fitBounds(pts, {{padding:[30,30]}}); }};
  fitO(); setTimeout(fitO, 400);
  DATA.trips.forEach(t => {{
    const mm = L.map('map-'+t.key, {{scrollWheelZoom:false}}); tiles(mm);
    const p2 = [];
    t.markers.forEach(k => {{ pin([k.lat,k.lng], k.kind==='house'? t.acc : COLORS[k.kind], k.name, mm, k.kind==='house'); p2.push([k.lat,k.lng]); }});
    const fit = () => {{ mm.invalidateSize(); mm.fitBounds(p2, {{padding:[24,24], maxZoom: 12}}); }};
    fit(); setTimeout(fit, 400);
  }});
}}
if (document.readyState === 'complete') build(); else window.addEventListener('load', build);
</script>
</body>
</html>'''
(HERE / 'index.html').write_text(page, encoding='utf-8')
print('wrote index.html', len(page), 'bytes; photos for', list(photos.keys()))
