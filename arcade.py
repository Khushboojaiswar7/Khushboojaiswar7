import os, json, urllib.request
from collections import Counter
from datetime import date
from xml.sax.saxutils import escape

USER = os.environ["GH_USER"]
TOKEN = os.environ["GH_TOKEN"]

QUERY = """
query($login:String!){
  user(login:$login){
    name bio location
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

name = escape(u["name"] or USER)
bio = escape((u["bio"] or "")[:70])
loc = escape(u["location"] or "")
repos = u["repositories"]["nodes"]
top = repos[:5]

langs = Counter(r["primaryLanguage"]["name"] for r in repos if r["primaryLanguage"])
total = sum(langs.values()) or 1
lang_rows = langs.most_common(5)

cal = u["contributionsCollection"]["contributionCalendar"]
weeks = cal["weeks"][-26:]
days = [d for w in weeks for d in w["contributionDays"]]
streak = 0
for d in reversed(days):
    if d["contributionCount"] > 0:
        streak += 1
    elif d["date"] != str(date.today()):
        break
score = sum(d["contributionCount"] for d in days)

BG, PANEL, TXT, DIM = "#0a0e27", "#11183a", "#e6e9ff", "#7a83b8"
GREEN, YELLOW, BLUE = "#3ddc84", "#ffd24a", "#4a90e2"


def level(n):
    if n == 0: return "#1a2236"
    if n < 3: return "#1f6f43"
    if n < 6: return "#2fb760"
    if n < 10: return "#3ddc84"
    return YELLOW


o = []
a = o.append
a(f'<svg xmlns="http://www.w3.org/2000/svg" width="820" height="720" viewBox="0 0 820 720" font-family="Courier New, monospace">')
a(f'<rect width="820" height="720" rx="16" fill="{BG}"/>')

# Title marquee
a(f'<rect x="150" y="20" width="520" height="50" rx="6" fill="{BLUE}"/>')
a(f'<text x="410" y="54" text-anchor="middle" font-size="28" font-weight="bold" fill="#0a0e27">{name.upper()}</text>')

# Player card
a(f'<rect x="30" y="90" width="760" height="110" rx="12" fill="{PANEL}" stroke="#2a3366" stroke-width="3"/>')
a(f'<text x="50" y="118" font-size="13" fill="{YELLOW}">PLAYER 1</text>')
a(f'<text x="770" y="118" text-anchor="end" font-size="13" fill="#ff5c5c">INSERT COIN</text>')
a(f'<text x="50" y="150" font-size="24" font-weight="bold" fill="{TXT}">{name}</text>')
a(f'<text x="50" y="174" font-size="13" fill="{TXT}">{bio}</text>')
a(f'<text x="50" y="192" font-size="11" fill="{DIM}">{loc} · {u["followers"]["totalCount"]} followers · {u["repositories"]["totalCount"]} repositories</text>')

# Hi-scores
a(f'<rect x="30" y="215" width="760" height="190" rx="12" fill="{PANEL}"/>')
a(f'<text x="410" y="245" text-anchor="middle" font-size="22" fill="{GREEN}">HI-SCORES</text>')
for i, r in enumerate(top):
    y = 282 + i * 28
    a(f'<text x="180" y="{y}" font-size="18" fill="{DIM}">{i+1}</text>')
    a(f'<text x="220" y="{y}" font-size="18" fill="{TXT}">{escape(r["name"].upper())[:26]}</text>')
    a(f'<text x="640" y="{y}" text-anchor="end" font-size="18" fill="{YELLOW}">{r["stargazerCount"]}</text>')

# Power-ups
a(f'<rect x="30" y="420" width="760" height="150" rx="12" fill="{PANEL}"/>')
a(f'<text x="50" y="446" font-size="13" fill="{TXT}">POWER-UPS</text>')
for i, (l, c) in enumerate(lang_rows):
    y = 475 + i * 20
    pct = round(c * 100 / total)
    filled = round(pct / 100 * 20)
    a(f'<text x="50" y="{y}" font-size="13" fill="{TXT}">{escape(l)}</text>')
    for k in range(20):
        col = BLUE if k < filled else "#1a2236"
        a(f'<rect x="{200 + k*22}" y="{y-11}" width="16" height="12" fill="{col}"/>')
    a(f'<text x="760" y="{y}" text-anchor="end" font-size="12" fill="{DIM}">{pct}%</text>')

# Level map
a(f'<rect x="30" y="585" width="760" height="115" rx="12" fill="{PANEL}"/>')
a(f'<text x="50" y="610" font-size="13" fill="{TXT}">LEVEL MAP  26 WEEKS</text>')
for wi, w in enumerate(weeks):
    for di, d in enumerate(w["contributionDays"]):
        a(f'<rect x="{50 + wi*14}" y="{622 + di*10}" width="11" height="8" fill="{level(d["contributionCount"])}"/>')
a(f'<text x="450" y="635" font-size="10" fill="{DIM}">COMBO</text>')
a(f'<text x="450" y="655" font-size="18" fill="{TXT}">{streak} days</text>')
a(f'<text x="450" y="675" font-size="10" fill="{DIM}">SCORE (26 WEEKS)</text>')
a(f'<text x="450" y="693" font-size="18" fill="{TXT}">{score:,}</text>')

a("</svg>")
open("arcade.svg", "w").write("\n".join(o))
print("arcade.svg written")




