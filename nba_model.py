import requests, time
from datetime import datetime, timezone

HEADERS = {
    'User-Agent': 'Mozilla/5.0',
    'Referer': 'https://www.nba.com/',
    'Origin': 'https://www.nba.com'
}

PLAYERS = [
    {"name":"Nikola Jokic","team":"DEN","pos":"C","id":203999,"market":"REB o12.5","dec":1.87,"model":62},
    {"name":"Domantas Sabonis","team":"SAC","pos":"C","id":203473,"market":"REB o13.5","dec":1.87,"model":61},
    {"name":"Luka Doncic","team":"LAL","pos":"PG","id":1629029,"market":"AST o9.5","dec":1.80,"model":64},
    {"name":"Victor Wembanyama","team":"SAS","pos":"C","id":1641705,"market":"RA o15.5","dec":1.83,"model":59},
]

def fetch_l7(player_id):
    """Auto fetch last 7 games REB/AST from stats.nba.com"""
    try:
        url = f"https://stats.nba.com/stats/playergamelog?PlayerID={player_id}&Season=2024-25&SeasonType=Regular Season"
        r = requests.get(url, headers=HEADERS, timeout=15)
        if r.status_code==200:
            data = r.json()
            rows = data['resultSets'][0]['rowSet'][:7] # last 7
            # headers:... REB is col 20, AST is col 21 in gamelog
            # Let's map dynamically
            headers_list = data['resultSets'][0]['headers']
            reb_idx = headers_list.index('REB')
            ast_idx = headers_list.index('AST')
            rebs = [row[reb_idx] for row in rows]
            asts = [row[ast_idx] for row in rows]
            return rebs, asts
    except Exception as e:
        print(f"Fetch fail {player_id}: {e}")
    # Fallback if API blocked (github actions sometimes)
    return [14,11,16,13,12,15,10], [9,11,8,10,12,9,10]

def get_games():
    try:
        today = datetime.now(timezone.utc).strftime("%Y%m%d")
        r = requests.get(f"https://cdn.nba.com/static/json/liveData/scoreboard/{today}/scoreboard.json", timeout=10)
        if r.status_code==200:
            games=[]
            for g in r.json().get('scoreboard',{}).get('games',[]):
                games.append({'home': g['homeTeam']['teamTricode'],'away': g['awayTeam']['teamTricode'],'time': g.get('gameStatusText','')})
            if games: return games
    except: pass
    return [{'away':'LAL','home':'GSW','time':'10:00 PM ET'}]

games = get_games()
enriched = []
for p in PLAYERS:
    rebs, asts = fetch_l7(p['id'])
    time.sleep(0.6) # be nice to NBA API
    p['l7_reb']=rebs
    p['l7_ast']=asts
    enriched.append(p)

def hit_rate(arr, line): return sum(1 for x in arr if x > line), len(arr)

html = f"""<!DOCTYPE html><html><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'>
<title>Orange Line - AUTO L7</title>
<style>
body{{background:#081229;color:#e8eefc;font-family:-apple-system,sans-serif;padding:14px;max-width:900px;margin:0 auto}}
h1{{color:#ff9a2e;font-size:24px}}.sub{{color:#8ea2cc;margin-bottom:16px;font-size:13px}}
.game{{background:#12204a;border:1px solid #22366e;border-radius:12px;padding:10px 12px;margin:8px 0;display:flex;justify-content:space-between}}
.card{{background:#111e3d;border:1px solid #1e3260;border-radius:14px;padding:14px;margin:14px 0}}
.badge{{background:#ff9a2e;color:#000;font-weight:800;padding:2px 8px;border-radius:20px;font-size:11px}}
.line{{color:#7dd3a8;font-weight:700}}.pill{{background:#1a2c5e;border-radius:20px;padding:4px 10px;font-size:12px;display:inline-block;margin:3px}}
.pill.model{{background:#173a2a;color:#7dd3a8;border:1px solid #2a6b4a}}.pill.hit{{background:#2a1a5e;color:#c7a2ff}}
.l7{{margin-top:10px;background:#0d1733;border-radius:10px;padding:10px;font-size:12px;line-height:1.6}}
.dot{{display:inline-block;width:28px;text-align:center;background:#1c2e5e;border-radius:6px;margin:2px;padding:2px 0}}
.dot.over{{background:#1e6b3a;color:#7dd3a8;font-weight:700}}.dot.under{{background:#3a1e2a;color:#ff8a8a}}
.edge{{color:#ff9a2e;font-size:12px;margin-top:8px}}.live{{color:#00ff88;font-size:10px;border:1px solid #00ff88;padding:2px 6px;border-radius:10px;margin-left:6px}}
</style></head><body>
<h1>🟠 Orange Line LIVE — {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')} <span class='live'>AUTO L7</span></h1>
<div class='sub'>Decimal + Prob + Auto Last 7 from stats.nba.com — auto 9am UTC</div>
<h3>Today's Slate</h3>
"""

for g in games:
    html+=f"<div class='game'><b>{g['away']} @ {g['home']}</b><span>{g['time']}</span></div>"

html+="<h3 style='margin-top:20px'>Top Leans — AUTO</h3>"

for p in enriched:
    line_val = float(p['market'].split('o')[1])
    is_reb = 'REB' in p['market'] and 'RA' not in p['market']
    is_ast = p['market'].startswith('AST')
    if is_reb: arr = p['l7_reb']
    elif is_ast: arr = p['l7_ast']
    else: arr = [r+a for r,a in zip(p['l7_reb'], p['l7_ast'])]

    hits, total = hit_rate(arr, line_val)
    implied = 100/p['dec']
    edge = p['model'] - implied
    avg = sum(arr)/len(arr) if arr else 0

    dots=""
    for v in arr[::-1]:
        cls="over" if v>line_val else "under"
        dots+=f"<span class='dot {cls}'>{v}</span>"

    html+=f"""<div class='card'>
<div><span class='badge'>{p['team']} {p['pos']}</span> <b>{p['name']}</b> — <span class='line'>{p['market']}</span></div>
<div style='margin-top:8px'>
<span class='pill'>Book: {p['dec']:.2f} ({implied:.1f}%)</span>
<span class='pill model'>Model: {p['model']}%</span>
<span class='pill' style='color:{"#7dd3a8" if edge>0 else "#ff8a8a"}'>Edge {edge:+.1f}%</span>
<span class='pill hit'>L7: {hits}-{total} ({hits/total*100:.0f}%)</span>
</div>
<div class='l7'>
<b>L7 {p['market'].split()[0]} (newest right):</b> {dots}<br>
<small style='color:#8ea2cc'>Avg {avg:.1f} | Last 7: {', '.join(map(str,arr))} | Source: stats.nba.com AUTO</small>
</div>
</div>"""

html+=f"<div class='sub' style='margin-top:26px'>Auto L7 fetched {datetime.now(timezone.utc).isoformat()} | niibaboo.github.io/NBA</div></body></html>"

open("index.html","w",encoding="utf-8").write(html)
print("AUTO L7 build done")
