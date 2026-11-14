import os, re, shutil, json, base64, random, textwrap, urllib.request
from urllib.parse import quote
from collections import Counter
from datetime import date
from xml.sax.saxutils import escape

# =====================================================
#  EDIT THIS BLOCK WITH YOUR OWN DETAILS
# =====================================================
ABOUT = ("Hi! I'm a developer who loves building AI and web projects. "
         "I'm currently learning new tools every week and working on "
         "projects that solve real problems.")

SKILLS = [            # (skill name, level 0-100)
    ("Python", 85),
    ("JavaScript", 60),
    ("HTML", 80),
    ("CSS", 70),
    ("Git", 65),
]

MAX_PROJECTS = 10     # how many repos to show (all public repos, newest first)

# OPTIONAL: override the text of a project. Leave empty to use the
# description and language from the repo itself.
PROJECTS = [          # (repo name, one-line description, tech used)
    # ("MedPal", "Your own one-line description.", "Python · Flask"),
]

CONTACT = [          # (button text, link)
    ("GitHub", "https://github.com/Khushboojaiswar7"),
    ("LinkedIn", "https://linkedin.com/in/yourname"),
    ("Email", "mailto:you@email.com"),
]
# =====================================================

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
      nodes{name description pushedAt stargazerCount primaryLanguage{name}}
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
stars = {r["name"].lower(): r["stargazerCount"] for r in repos}
top = repos[:5]

over = {p[0].lower(): p for p in PROJECTS}
proj_src = sorted((r for r in repos if r["name"].lower() != USER.lower()),
                  key=lambda r: r["pushedAt"] or "", reverse=True)[:MAX_PROJECTS]
projects = []
for r in proj_src:
    k = r["name"].lower()
    lang = r["primaryLanguage"]["name"] if r["primaryLanguage"] else "-"
    if k in over:
        projects.append((r["name"], over[k][1], over[k][2], r["stargazerCount"]))
    else:
        projects.append((r["name"], r["description"] or "No description yet.", lang, r["stargazerCount"]))

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
      "C": "#888888", "Vue": "#41b883", "React": "#61dafb", "Git": "#f05032",
      "SQL": "#e38c00", "MySQL": "#00758f", "Flask": "#9aa4c7", "Node": "#68a063",
      "Jupyter Notebook": "#da5b0b", "Dart": "#00b4ab", "Go": "#00add8"}


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


def wrap(text, width, maxlines):
    return [escape(l) for l in textwrap.wrap(text, width)[:maxlines]]


o = []
a = o.append

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

y = 490


def panel(y, h, edge=True):
    s = f' stroke="{EDGE}" stroke-width="4"' if edge else ""
    a(f'<rect x="30" y="{y}" width="760" height="{h}" rx="14" fill="{PANEL}"{s}/>')


# ===== PLAYER CARD =====
panel(y, 130)
a(f'<text x="55" y="{y+28}" font-size="13" fill="{YELLOW}">PLAYER 1</text>')
a(f'<text x="640" y="{y+28}" text-anchor="end" font-size="13" fill="{RED}">INSERT COIN</text>')
a(f'<text x="55" y="{y+58}" font-size="24" font-weight="bold" fill="{TXT}">{name}</text>')
for k, line in enumerate(bio_lines):
    a(f'<text x="55" y="{y+80+k*18}" font-size="13" fill="{TXT}">{line}</text>')
a(f'<text x="55" y="{y+116}" font-size="11" fill="{DIM}">{meta}</text>')
a(f'<rect x="662" y="{y+16}" width="100" height="100" fill="none" stroke="#ffffff" stroke-width="3"/>')
if av:
    a(f'<image href="{av}" x="666" y="{y+20}" width="92" height="92" style="image-rendering:pixelated"/>')
y += 150

# ===== ABOUT =====
lines = wrap(ABOUT, 78, 5)
h = 56 + len(lines) * 22
panel(y, h, edge=False)
a(f'<text x="55" y="{y+32}" font-size="16" fill="{GREEN}">ABOUT PLAYER</text>')
for k, line in enumerate(lines):
    a(f'<text x="55" y="{y+62+k*22}" font-size="14" fill="{TXT}">{line}</text>')
y += h + 20

# ===== HI-SCORES =====
h = 66 + len(top) * 28
panel(y, h, edge=False)
a(f'<text x="410" y="{y+36}" text-anchor="middle" font-size="24" fill="{GREEN}">HI-SCORES</text>')
for i, r in enumerate(top):
    ry = y + 76 + i * 28
    lang = r["primaryLanguage"]["name"] if r["primaryLanguage"] else ""
    a(f'<text x="190" y="{ry}" font-size="18" fill="{DIM}">{i+1}</text>')
    if lang:
        a(badge(222, ry, lang))
    a(f'<text x="252" y="{ry}" font-size="18" fill="{TXT}">{escape(r["name"].upper())[:24]}</text>')
    a(f'<text x="640" y="{ry}" text-anchor="end" font-size="18" fill="{YELLOW}">{r["stargazerCount"]}</text>')
y += h + 20

# ===== POWER-UPS (SKILLS) =====
h = 50 + len(SKILLS) * 24
panel(y, h)
a(f'<text x="55" y="{y+30}" font-size="13" fill="{TXT}">POWER-UPS  (SKILLS)</text>')
for i, (sk, pct) in enumerate(SKILLS):
    ry = y + 62 + i * 24
    filled = round(pct / 100 * 20)
    col = LC.get(sk, BLUE)
    a(badge(55, ry, sk))
    a(f'<text x="85" y="{ry}" font-size="13" fill="{TXT}">{escape(sk)[:14]}</text>')
    for k in range(20):
        a(f'<rect x="{250 + k*22}" y="{ry-11}" width="16" height="12" fill="{col if k < filled else "#141a33"}"/>')
    a(f'<text x="765" y="{ry}" text-anchor="end" font-size="12" fill="{DIM}">{pct}%</text>')
y += h + 20

# ===== PROJECT CARDS (separate images, each one clickable) =====
shutil.rmtree("cards", ignore_errors=True)
os.makedirs("cards")
card_html = []
for pn, pd, pt, pstars in projects:
    fn = re.sub(r"[^A-Za-z0-9_.-]", "_", pn)
    c = ['<svg xmlns="http://www.w3.org/2000/svg" width="820" height="100" viewBox="0 0 820 100" font-family="Courier New, monospace">',
         f'<rect width="820" height="100" fill="{BG}"/>',
         f'<rect x="30" y="8" width="760" height="84" rx="12" fill="#111838" stroke="{EDGE}" stroke-width="3"/>',
         f'<text x="50" y="34" font-size="17" font-weight="bold" fill="{YELLOW}">{escape(pn.upper())[:34]}</text>',
         f'<text x="770" y="34" text-anchor="end" font-size="13" fill="{DIM}">★ {pstars}</text>']
    for k, line in enumerate(wrap(pd, 80, 2)):
        c.append(f'<text x="50" y="{54+k*16}" font-size="12" fill="{TXT}">{line}</text>')
    c.append(f'<text x="50" y="86" font-size="11" fill="{GREEN}">TECH: {escape(pt)}</text>')
    c.append(f'<text x="770" y="86" text-anchor="end" font-size="11" fill="{YELLOW}">PRESS START ▶</text>')
    c.append("</svg>")
    open(f"cards/{fn}.svg", "w", encoding="utf-8").write("\n".join(c))
    card_html.append(f'<a href="https://github.com/{USER}/{pn}"><img src="cards/{fn}.svg" alt="{escape(pn)}" width="820"></a>')

# ===== LEVEL MAP =====
panel(y, 120)
a(f'<text x="55" y="{y+28}" font-size="13" fill="{TXT}">LEVEL MAP  26 WEEKS</text>')
for wi, w in enumerate(weeks):
    for di, d in enumerate(w["contributionDays"]):
        a(f'<rect x="{55 + wi*14}" y="{y+40+di*10}" width="11" height="8" fill="{level(d["contributionCount"])}"/>')
for lx, ly, label, val in [(470, y+46, "COMBO", f"{streak} days"),
                           (470, y+86, "BEST COMBO", f"{best} days"),
                           (620, y+46, "SCORE (26 WEEKS)", f"{score:,}")]:
    a(f'<text x="{lx}" y="{ly}" font-size="10" fill="{DIM}">{label}</text>')
    a(f'<text x="{lx}" y="{ly+20}" font-size="18" fill="{TXT}">{val}</text>')
y += 140

# ===== CONTACT BUTTONS + README UPDATE =====
LOGO = {"github": "github", "linkedin": "linkedin", "email": "gmail"}
btns = []
for label, url in CONTACT:
    lg = LOGO.get(label.lower(), "")
    img = f"https://img.shields.io/badge/{quote(label)}-3b82d6?style=for-the-badge" + (f"&logo={lg}&logoColor=white" if lg else "")
    btns.append(f'<a href="{url}"><img src="{img}" alt="{escape(label)}"></a>')
block = ("<!--MISSIONS-->\n<div align=\"center\">\n<h2>MISSIONS (click a card to open it)</h2>\n"
         + "\n".join(card_html) + "\n<h2>CONTINUE?</h2>\n" + " ".join(btns) + "\n</div>\n<!--/MISSIONS-->")
txt = open("README.md", encoding="utf-8").read() if os.path.exists("README.md") else "![Arcade](arcade.svg)\n"
if "<!--MISSIONS-->" in txt and "<!--/MISSIONS-->" in txt:
    txt = re.sub(r"<!--MISSIONS-->.*?<!--/MISSIONS-->", lambda m: block, txt, flags=re.S)
else:
    txt = txt.rstrip() + "\n\n" + block + "\n"
open("README.md", "w", encoding="utf-8").write(txt)

H = y
head = (f'<svg xmlns="http://www.w3.org/2000/svg" width="820" height="{H}" viewBox="0 0 820 {H}" '
        f'font-family="Courier New, monospace"><rect width="820" height="{H}" rx="16" fill="{BG}"/>')
open("arcade.svg", "w").write(head + "\n".join(o) + "</svg>")
print("arcade.svg written")


