import os, json, base64, random, textwrap, urllib.request
from collections import Counter
from datetime import date
from xml.sax.saxutils import escape

USER = os.environ["GH_USER"]
TOKEN = os.environ["GH_TOKEN"]

QUERY = """
query($login:String!){
  user(login:$login){
    name bio location company avatarUrl
    followers{totalCount}
    repositories(ownerAffiliations:OWNER,isFork:false,first:100,
                 orderBy:{field:STARGAZERS,direction:DESC}){
      totalCount
      nodes{name stargazerCount primaryLanguage{name}}
    }
    contributionsCollection{contributionCalendar{
      totalContributions
      weeks{contributionDays{contributionCount date}}
    }}
  }
}"""

req = urllib.request.Request(
    "https://api.github.com/graphql",
    data=json.dumps({"query": QUERY, "variables": {"login": USER}}).encode(),
    headers={"Authorization": f"bearer {TOKEN}"},
)
resp = json.load(urllib.request.urlopen(req))
if "data" not in resp:
    raise SystemExit("API ERROR: " + json.dumps(resp))
u = resp["data"]["user"]

# ---------- data ----------
name = escape(u["name"] or USER)
bio_lines = [escape(l) for l in textwrap.wrap(u["bio"] or "", 62)[:2]]
repos = u["repositories"]["nodes"]
top = repos[:5]
langs = Counter(r["primaryLanguage"]["name"] for r in repos if r["primaryLanguage"])
ltotal = sum(langs.values()) or 1
lang_rows = langs.most_common(5)

weeks = u["contributionsCollection"]["contributionCalendar"]["weeks"][-26:]
days = [d for w in weeks for d in w["contributionDays"]]
weekly = [sum(d["contributionCount"] for d in w["contributionDays"]) for w in weeks]
score = sum(weekly)
mx = max(weekly) or 1
coins = {i for i in sorted(range(len(weekly)), key=lambda i: -weekly[i])[:5] if weekly[i] > 0}

best = run = 0
for d in days:
    run = run + 1 if d["contributionCount"] > 0 else 0
    best = max(best, run)
streak = 0
for d in reversed(days):
    if d["contributionCount"] > 0:
        streak += 1
    elif d["date"] != str(date.today()):
        break

meta = " · ".join(x for x in [
    escape(u["location"] or ""), escape(u["company"] or ""),
    f'{u["followers"]["totalCount"]} followers',
    f'{u["repositories"]["totalCount"]} repositories'] if x)

# avatar as tiny pixelated embedded image
try:
    r = urllib.request.urlopen(u["avatarUrl"] + "&s=32")
    av = "data:%s;base64,%s" % (r.headers.get_content_type(), base64.b64encode(r.read()).decode())
except Exception:
    av = ""

# ---------- style ----------
BG, PANEL, EDGE = "#05071a", "#0d1230", "#232a5c"
TXT, DIM = "#e6e9ff", "#7a83b8"
GREEN, YELLOW, BLUE, RED = "#3ddc84", "#ffd24a", "#3b82d6", "#ff5c5c"
LC = {"Python": "#3776ab", "JavaScript": "#f7df1e", "TypeScript": "#3178c6",
      "HTML": "#e34c26", "CSS": "#563d7c", "Java": "#b07219", "C++": "#f34b7d",
      "C": "#888888", "Vue": "#41b883", "Jupyter Notebook": "#da5b0b",
      "Dart": "#00b4ab", "Go": "#00add8", "Rust": "#dea584", "Kotlin": "#a97bff"}


def level(n):
    if n == 0: return "#141a33"
    if n < 3: return "#1f6f43"
    if n < 6: return "#2fb760"
    if n < 10: return "#3ddc84"
    return YELLOW


def badge(x, y, lang):
    c = LC.get(lang, "#8892b0")
    return (f'<rect x="{x}" y="{y-12}" width="20" height="15" rx="3" fill="{c}"/>'
            f'<text x="{x+10}" y="{y-1}" text-anchor="middle" font-size="9" '
            f'font-weight="bold" fill="#0a0e27">{escape(lang[:2].upper())}</text>')


H = 1180
o = []
a = o.append
a(f'<svg xmlns="http://www.w3.org/2000/svg" width="820" height="{H}" viewBox="0 0 820 {H}" font-family="Courier New, monospace">')
a(f'<rect width="820" height="{H}" rx="16" fill="{BG}"/>')

# ===== ARCADE CABINET =====
a(f'<rect x="150" y="20" width="520" height="56" rx="4" fill="{BLUE}"/>')
a(f'<text x="410" y="58" text-anchor="middle" font-size="28" font-weight="bold" fill="#0a0e27">{name.upper()}</text>')
a('<polygon points="130,76 690,76 690,332 130,332" fill="#1b2145"/>')
a('<rect x="160" y="96" width="500" height="236" rx="8" fill="#03041a" stroke="#0b0f2e" stroke-width="6"/>')
random.seed(7)
for _ in range(45):
    a(f'<circle cx="{random.randint(168,652)}" cy="{random.randint(104,320)}" r="{random.choice([0.8,1,1.3])}" fill="#8fa0ff" opacity="0.7"/>')
a(f'<text x="176" y="122" font-size="14" fill="{TXT}">SCORE {score}</text>')
a(f'<text x="640" y="122" text-anchor="end" font-size="14" fill="{RED}">1UP</text>')
step = 460 / 26
for i, v in enumerate(weekly):
    h = 8 + (v / mx) * 140
    x = 180 + i * step
    y = 318 - h
    a(f'<rect x="{x:.1f}" y="{y:.1f}" width="{step-4:.1f}" height="{h:.1f}" fill="{BLUE}"/>')
    if i in coins:
        a(f'<rect x="{x+step/2-6:.1f}" y="{y-18:.1f}" width="8" height="8" fill="{YELLOW}"/>')
i = len(weekly) - 4
sx = 180 + i * step + step / 2 - 2
sy = 318 - (8 + (weekly[i] / mx) * 140) - 36
a(f'<polygon points="{sx:.1f},{sy:.1f} {sx+8:.1f},{sy+16:.1f} {sx-8:.1f},{sy+16:.1f}" fill="#ffffff"/>')

a('<polygon points="130,332 690,332 730,392 90,392" fill="#2a3170"/>')
a(f'<circle cx="230" cy="350" r="8" fill="{RED}"/><circle cx="230" cy="374" r="12" fill="#111"/>')
a(f'<text x="352" y="372" font-size="11" fill="{BLUE}">P1</text>')
a(f'<rect x="384" y="338" width="52" height="52" fill="none" stroke="{BLUE}" stroke-width="3"/>')
if av:
    a(f'<image href="{av}" x="387" y="341" width="46" height="46" style="image-rendering:pixelated"/>')
for cx, col in [(480, "#e8b84a"), (512, "#4ac26b"), (544, "#5aa0ff")]:
    a(f'<circle cx="{cx}" cy="368" r="10" fill="{col}"/>')
a('<rect x="170" y="392" width="480" height="50" fill="#1b2145"/>')
a(f'<text x="410" y="420" text-anchor="middle" font-size="16" fill="{YELLOW}">INSERT COIN</text>')
a(f'<text x="410" y="434" text-anchor="middle" font-size="8" fill="{DIM}">github.com/{escape(USER)}</text>')
a('<rect x="170" y="442" width="40" height="28" fill="#151a3a"/><rect x="610" y="442" width="40" height="28" fill="#151a3a"/>')

# ===== PLAYER CARD =====
y0 = 490
a(f'<rect x="30" y="{y0}" width="760" height="130" rx="14" fill="{PANEL}" stroke="{EDGE}" stroke-width="4"/>')
a(f'<text x="55" y="{y0+28}" font-size="13" fill="{YELLOW}">PLAYER 1</text>')
a(f'<text x="640" y="{y0+28}" text-anchor="end" font-size="13" fill="{RED}">INSERT COIN</text>')
a(f'<text x="55" y="{y0+58}" font-size="24" font-weight="bold" fill="{TXT}">{name}</text>')
for k, line in enumerate(bio_lines):
    a(f'<text x="55" y="{y0+80+k*18}" font-size="13" fill="{TXT}">{line}</text>')
a(f'<text x="55" y="{y0+116}" font-size="11" fill="{DIM}">{meta}</text>')
a(f'<rect x="662" y="{y0+16}" width="100" height="100" fill="none" stroke="#ffffff" stroke-width="3"/>')
if av:
    a(f'<image href="{av}" x="666" y="{y0+20}" width="92" height="92" style="image-rendering:pixelated"/>')

# ===== HI-SCORES =====
y0 = 640
a(f'<rect x="30" y="{y0}" width="760" height="210" rx="14" fill="{PANEL}"/>')
a(f'<text x="410" y="{y0+36}" text-anchor="middle" font-size="24" fill="{GREEN}">HI-SCORES</text>')
for i, r in enumerate(top):
    y = y0 + 76 + i * 28
    lang = r["primaryLanguage"]["name"] if r["primaryLanguage"] else ""
    a(f'<text x="190" y="{y}" font-size="18" fill="{DIM}">{i+1}</text>')
    if lang:
        a(badge(222, y, lang))
    a(f'<text x="252" y="{y}" font-size="18" fill="{TXT}">{escape(r["name"].upper())[:24]}</text>')
    a(f'<text x="640" y="{y}" text-anchor="end" font-size="18" fill="{YELLOW}">{r["stargazerCount"]}</text>')

# ===== POWER-UPS =====
y0 = 870
a(f'<rect x="30" y="{y0}" width="760" height="150" rx="14" fill="{PANEL}" stroke="{EDGE}" stroke-width="4"/>')
a(f'<text x="55" y="{y0+30}" font-size="13" fill="{TXT}">POWER-UPS</text>')
for i, (l, c) in enumerate(lang_rows):
    y = y0 + 62 + i * 22
    pct = round(c * 100 / ltotal)
    filled = round(pct / 100 * 20)
    col = LC.get(l, "#8892b0")
    a(badge(55, y, l))
    a(f'<text x="85" y="{y}" font-size="13" fill="{TXT}">{escape(l)[:14]}</text>')
    for k in range(20):
        a(f'<rect x="{250 + k*22}" y="{y-11}" width="16" height="12" fill="{col if k < filled else "#141a33"}"/>')
    a(f'<text x="765" y="{y}" text-anchor="end" font-size="12" fill="{DIM}">{pct}%</text>')

# ===== LEVEL MAP =====
y0 = 1040
a(f'<rect x="30" y="{y0}" width="760" height="120" rx="14" fill="{PANEL}" stroke="{EDGE}" stroke-width="4"/>')
a(f'<text x="55" y="{y0+28}" font-size="13" fill="{TXT}">LEVEL MAP  26 WEEKS</text>')
for wi, w in enumerate(weeks):
    for di, d in enumerate(w["contributionDays"]):
        a(f'<rect x="{55 + wi*14}" y="{y0+40+di*10}" width="11" height="8" fill="{level(d["contributionCount"])}"/>')
for lx, ly, label, val in [(470, y0+46, "COMBO", f"{streak} days"),
                           (470, y0+86, "BEST COMBO", f"{best} days"),
                           (620, y0+46, "SCORE (26 WEEKS)", f"{score:,}")]:
    a(f'<text x="{lx}" y="{ly}" font-size="10" fill="{DIM}">{label}</text>')
    a(f'<text x="{lx}" y="{ly+20}" font-size="18" fill="{TXT}">{val}</text>')

a("</svg>")
open("arcade.svg", "w").write("\n".join(o))
print("arcade.svg written")



