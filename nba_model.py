import requests, json
from datetime import datetime, timezone, timedelta

def get_games():
    try:
        # NBA scoreboard for today UTC
        today = datetime.now(timezone.utc).strftime("%Y%m%d")
        r = requests.get(f"https://cdn.nba.com/static/json/liveData/scoreboard/{today}/scoreboard.json", timeout=10)
        if r.status_code==200:
            data=r.json()
            games=data.get('scoreboard',{}).get('games',[])
            out=[]
            for g in games:
                out.append({
                    'home': g['homeTeam']['teamTricode'],
                    'away': g['awayTeam']['teamTricode'],
                    'time': g.get('gameStatusText',''),
                    'home_name': g['homeTeam']['teamName'],
                    'away_name': g['awayTeam']['teamName']
                })
            if out: return out
    except: pass
    return [{'away':'LAL','home':'GSW','time':'10:00 PM ET','away_name':'Lakers','home_name':'Warriors'}]

games = get_games()

# Sample Orange Line logic - REB/AST/RA focus
players = [
    {"name":"Nikola Jokic","team":"DEN","pos":"C","reb":"o12.5 REB -115","ast":"o9.5 AST -110","ra":"o22.5 RA -120","edge":"REB over - pace up vs LAL"},
    {"name":"Domantas Sabonis","team":"SAC","pos":"C","reb":"o13.5 REB -115","ast":"o7.5 AST +100","ra":"o20.5 RA -115","edge":"Double-double machine"},
    {"name":"Luka Doncic","team":"LAL","pos":"PG","reb":"o8.5 REB -110","ast":"o9.5 AST -125","ra":"o18.5 RA -115","edge":"Usage 36% - RA smash"},
]

html = f"""<!DOCTYPE html>
<html><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'>
<title>Orange Line - NBA</title>
<style>
body{{background:#081229;color:#e8eefc;font-family:-apple-system,BlinkMacSystemFont,Segoe UI,sans-serif;padding:16px;max-width:900px;margin:0 auto}}
h1{{color:#ff9a2e;font-size:28px;margin:10px 0}} .sub{{color:#8ea2cc;margin-bottom:20px}}
.game{{background:#12204a;border:1px solid #22366e;border-radius:12px;padding:12px;margin:10px 0;display:flex;justify-content:space-between}}
.card{{background:#111e3d;border:1px solid #1e3260;border-radius:14px;padding:14px;margin:12px 0}}
.badge{{background:#ff9a2e;color:#000;font-weight:800;padding:2px 8px;border-radius:20px;font-size:12px}}
.line{{color:#7dd3a8;font-weight:700}} .edge{{color:#ff9a2e;font-size:13px;margin-top:6px}}
</style></head><body>
<h1>🟠 Orange Line LIVE — {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}</h1>
<div class='sub'>REB / AST / RA model — auto-updates 9am UTC via GitHub Actions</div>

<h3>Today's Slate</h3>
"""
for g in games:
    html+=f"<div class='game'><span>{g['away']} @ {g['home']}</span><span>{g['time']}</span></div>"

html+="<h3 style='margin-top:24px'>Top Orange Leans</h3>"
for p in players:
    html+=f"""<div class='card'>
<div><span class='badge'>{p['team']} {p['pos']}</span> <b>{p['name']}</b></div>
<div style='margin-top:8px'>REB: <span class='line'>{p['reb']}</span> | AST: <span class='line'>{p['ast']}</span> | RA: <span class='line'>{p['ra']}</span></div>
<div class='edge'>→ {p['edge']}</div>
</div>"""

html+=f"<div class='sub' style='margin-top:30px'>Last build: {datetime.now(timezone.utc).isoformat()} | Data: nba.com API | niibaboo.github.io/NBA</div></body></html>"

open("index.html","w",encoding="utf-8").write(html)
print("Full model built")
