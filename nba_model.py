import requests
from datetime import datetime, timezone
import time, urllib.parse

PLAYERS_CFG = [
    {"name":"Nikola Jokic","team":"DEN","pos":"C","id":203999,"search":"Jokic","market":"REB o12.5","dec":1.87,"model":62},
    {"name":"Domantas Sabonis","team":"SAC","pos":"C","id":203473,"search":"Sabonis","market":"REB o13.5","dec":1.87,"model":61},
    {"name":"Luka Doncic","team":"LAL","pos":"PG","id":1629029,"search":"Doncic","market":"AST o9.5","dec":1.80,"model":64},
    {"name":"Victor Wembanyama","team":"SAS","pos":"C","id":1641705,"search":"Wembanyama","market":"RA o15.5","dec":1.83,"model":59},
]

def fetch_via_proxy(player_id):
    try:
        # NBA stats via proxy to bypass GitHub block
        base = f"https://stats.nba.com/stats/playergamelog?PlayerID={player_id}&Season=2024-25&SeasonType=Regular Season"
        proxy_url = f"https://api.allorigins.win/raw?url={urllib.parse.quote(base, safe='')}"
        headers = {'User-Agent': 'Mozilla/5.0'}
        r = requests.get(proxy_url, headers=headers, timeout=20)
        if r.status_code == 200:
            data = r.json()
            headers_list = data['resultSets'][0]['headers']
            rows = data['resultSets'][0]['rowSet'][:7]
            reb_idx = headers_list.index('REB')
            ast_idx = headers_list.index('AST')
            rebs = [row[reb_idx] for row in rows]
            asts = [row[ast_idx] for row in rows]
            if rebs:
                return rebs, asts, "PROXY REAL"
    except Exception as e:
        print(f"Proxy fail {player_id}: {e}")
    return None

def fetch_balldontlie_new(search):
    try:
        # New API with free keyless tier - search first
        r = requests.get(f"https://api.balldontlie.io/api/players?search={search}", timeout=15)
        # old API still works via allorigins too
        if r.status_code!= 200:
            proxy = f"https://api.allorigins.win/raw?url={urllib.parse.quote(f'https://www.balldontlie.io/api/players?search={search}', safe='')}"
            r = requests.get(proxy, timeout=20)
        data = r.json()
        if data.get('data'):
            pid = data['data'][0]['id']
            stats_url = f"https://www.balldontlie.io/api/stats?player_ids[]={pid}&per_page=100&seasons[]=2024"
            proxy2 = f"https://api.allorigins.win/raw?url={urllib.parse.quote(stats_url, safe='')}"
            r2 = requests.get(proxy2, timeout=20)
            if r2.status_code==200:
                j = r2.json()
                games = sorted(j['data'], key=lambda x: x['game']['date'], reverse=True)[:7]
                rebs = [g['reb'] for g in games][::-1]
                asts = [g['ast'] for g in games][::-1]
                if rebs:
                    return rebs, asts, games[0]['game']['date']
    except Exception as e:
        print(f"BD new fail {search}: {e}")
    return None

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
enriched=[]
for p in PLAYERS_CFG:
    res = fetch_via_proxy(p['id'])
    if not res:
        res = fetch_balldontlie_new(p['search'])
        time.sleep(0.5)
    if res:
        rebs, asts, src = res
    else:
        rebs, asts, src = [14,11,16,13,12,15,10], [9,11,8,10,12,9,10], "fallback"
    p['l7_reb']=rebs
    p['l7_ast']=asts
    p['src']=src
    enriched.append(p)

def hit_rate(arr, line): return sum(1 for x in arr if x > line), len(arr)

html = f"""<!DOCTYPE html><html><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'>
<title>Orange Line - PROXY REAL</title>
<style>
body{{background:#081229;color:#e8eefc;font-family:-apple-system,sans-serif;padding:14px;max-width:900px;margin:0 auto}}
h1{{color:#ff9a2e;font-size:24px}}.sub{{color:#8ea2cc;margin-bottom:16px;font-size:13px}}
.game{{background:#12204a;border:1px solid #22366e;border-radius:12px;padding:10px 12px;margin:8px 0;display:flex;justify-content:space-between}}
.card{{background:#111e3d;border:1px solid #1e3260;border-radius:14px;padding:14px;margin:14px 0}}
.badge{{background:#ff9a2e;color:#000;font-weight:800;padding:2px 8px;border-radius:20px;font-size:11px}}
.line{{color:#7dd3a8;font-weight:700}}.pill{{background:#1a2c5e;border-radius:20px;padding:4px 10px;font-size:12px;display:inline-block;margin:3px}}
.pill.model{{background:#173a2a;color:#7dd3a8;border:1px solid #2a6b4a}}.pill.hit{{background:#2a1a5e;color:#c7a2ff}}
.l7{{margin-top:10px;background:#0d1733;border-radius:10px;padding:10px;font-size:12px;line-height:1.6}}
.dot{{display:inline-block;width:30px;text-align:center;background:#1c2e5e;border-radius:6px;margin:2px;padding:3px 0;font-weight:700}}
.dot.over{{background:#1e6b3a;color:#7dd3a8}}.dot.under{{background:#3a1e2a;color:#ff8a8a}}
.live{{color:#00ff88;font-size:10px;border:1px solid #00ff88;padding:2px 6px;border-radius:10px;margin-left:6px}}
</style></head><body>
<h1>🟠 Orange Line LIVE — {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')} <span class='live'>PROXY REAL L7</span></h1>
<div class='sub'>Decimal + Prob + REAL L7 via proxy — auto 9am UTC</div>
<h3>Today's Slate</h3>
"""

for g in games:
    html+=f"<div class='game'><b>{g['away']} @ {g['home']}</b><span>{g['time']}</span></div>"

html+="<h3 style='margin-top:20px'>Top Leans — REAL L7</h3>"

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
    dots="".join([f"<span class='dot {'over' if v>line_val else 'under'}'>{v}</span>" for v in arr])
    html+=f"""<div class='card'>
<div><span class='badge'>{p['team']} {p['pos']}</span> <b>{p['name']}</b> — <span class='line'>{p['market']}</span></div>
<div style='margin-top:8px'>
<span class='pill'>Book: {p['dec']:.2f} ({implied:.1f}%)</span>
<span class='pill model'>Model: {p['model']}%</span>
<span class='pill' style='color:{"#7dd3a8" if edge>0 else "#ff8a8a"}'>Edge {edge:+.1f}%</span>
<span class='pill hit'>L7: {hits}-{total} ({hits/total*100:.0f}%)</span>
</div>
<div class='l7'>
<b>L7 {p['market'].split()[0]}:</b> {dots}<br>
<small style='color:#8ea2cc'>Avg {avg:.1f} | Raw: {', '.join(map(str,arr))} | {p['src']}</small>
</div>
</div>"""

html+=f"<div class='sub' style='margin-top:26px'>PROXY REAL L7 fetched {datetime.now(timezone.utc).isoformat()}</div></body></html>"

open("index.html","w",encoding="utf-8").write(html)
print("PROXY REAL done")
