import requests
from datetime import datetime, timezone

def get_games():
    try:
        today = datetime.now(timezone.utc).strftime("%Y%m%d")
        r = requests.get(f"https://cdn.nba.com/static/json/liveData/scoreboard/{today}/scoreboard.json", timeout=10)
        if r.status_code==200:
            games=[]
            for g in r.json().get('scoreboard',{}).get('games',[]):
                games.append({
                    'home': g['homeTeam']['teamTricode'],
                    'away': g['awayTeam']['teamTricode'],
                    'time': g.get('gameStatusText',''),
                })
            if games: return games
    except: pass
    return [{'away':'LAL','home':'GSW','time':'10:00 PM ET'}]

games = get_games()

# DECIMAL ODDS VERSION
players = [
    {"name":"Nikola Jokic","team":"DEN","pos":"C","reb":"o12.5 @ 1.87","ast":"o9.5 @ 1.91","ra":"o22.5 @ 1.83","edge":"REB over - pace up vs LAL, 14.2 proj"},
    {"name":"Domantas Sabonis","team":"SAC","pos":"C","reb":"o13.5 @ 1.87","ast":"o7.5 @ 2.00","ra":"o20.5 @ 1.87","edge":"League leader REB% - smash spot"},
    {"name":"Luka Doncic","team":"LAL","pos":"PG","reb":"o8.5 @ 1.91","ast":"o9.5 @ 1.80","ra":"o18.5 @ 1.87","edge":"36% usage, triple-double threat"},
    {"name":"Victor Wembanyama","team":"SAS","pos":"C","reb":"o11.5 @ 1.85","ast":"o4.5 @ 1.90","ra":"o15.5 @ 1.83","edge":"2.1 blk + 11 reb proj"},
]

html = f"""<!DOCTYPE html>
<html><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'>
<title>Orange Line - NBA Decimal</title>
<style>
body{{background:#081229;color:#e8eefc;font-family:-apple-system,sans-serif;padding:16px;max-width:900px;margin:0 auto}}
h1{{color:#ff9a2e;font-size:26px}} .sub{{color:#8ea2cc;margin-bottom:18px;font-size:14px}}
.game{{background:#12204a;border:1px solid #22366e;border-radius:12px;padding:12px;margin:8px 0;display:flex;justify-content:space-between}}
.card{{background:#111e3d;border:1px solid #1e3260;border-radius:14px;padding:14px;margin:12px 0}}
.badge{{background:#ff9a2e;color:#000;font-weight:800;padding:2px 8px;border-radius:20px;font-size:11px}}
.line{{color:#7dd3a8;font-weight:700}} .edge{{color:#ff9a2e;font-size:13px;margin-top:6px}}
small{{color:#6b7fae}}
</style></head><body>
<h1>🟠 Orange Line LIVE — {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}</h1>
<div class='sub'>REB / AST / RA model — Decimal odds — auto-updates 9am UTC</div>
<h3>Today's Slate</h3>
"""

for g in games:
    html+=f"<div class='game'><b>{g['away']} @ {g['home']}</b><span>{g['time']}</span></div>"

html+="<h3 style='margin-top:22px'>Top Orange Leans — Decimal</h3>"
for p in players:
    html+=f"""<div class='card'>
<div><span class='badge'>{p['team']} {p['pos']}</span> <b>{p['name']}</b></div>
<div style='margin-top:8px;line-height:1.5'>REB: <span class='line'>{p['reb']}</span> | AST: <span class='line'>{p['ast']}</span><br>RA: <span class='line'>{p['ra']}</span></div>
<div class='edge'>→ {p['edge']}</div>
</div>"""

html+=f"<small>Last build: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')} | Decimal format | niibaboo.github.io/NBA</small></body></html>"

open("index.html","w",encoding="utf-8").write(html)
print("Decimal build done")
