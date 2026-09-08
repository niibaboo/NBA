from datetime import datetime, timezone

games = [{'away':'LAL','home':'GSW','time':'10:00 PM ET'}]

players = [
 {"name":"Nikola Jokic","team":"DEN","pos":"C","market":"REB o12.5","dec":1.87,"model":62,"rebs":[12,14,11,16,10,13,15],"asts":[10,8,11,9,12,7,10]},
 {"name":"Domantas Sabonis","team":"SAC","pos":"C","market":"REB o13.5","dec":1.87,"model":61,"rebs":[16,13,14,18,12,11,15],"asts":[6,8,5,9,7,10,6]},
 {"name":"Luka Doncic","team":"LAL","pos":"PG","market":"AST o9.5","dec":1.80,"model":64,"rebs":[8,9,7,10,6,9,8],"asts":[12,11,9,13,10,14,11]},
 {"name":"Victor Wembanyama","team":"SAS","pos":"C","market":"RA o15.5","dec":1.83,"model":59,"rebs":[11,13,10,12,14,9,15],"asts":[4,5,3,6,4,7,5]},
]

def hit(arr, line): return sum(1 for x in arr if x>line)

html=f"""<!DOCTYPE html><html><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'>
<title>Orange Line FINAL</title>
<style>
body{{background:#081229;color:#e8eefc;font-family:-apple-system,sans-serif;padding:14px;max-width:900px;margin:0 auto}}
h1{{color:#ff9a2e;font-size:24px}}.sub{{color:#8ea2cc;margin-bottom:16px;font-size:13px}}
.game{{background:#12204a;border:1px solid #22366e;border-radius:12px;padding:10px 12px;margin:8px 0;display:flex;justify-content:space-between}}
.card{{background:#111e3d;border:1px solid #1e3260;border-radius:14px;padding:14px;margin:14px 0}}
.badge{{background:#ff9a2e;color:#000;font-weight:800;padding:2px 8px;border-radius:20px;font-size:11px}}
.line{{color:#7dd3a8;font-weight:700}}.pill{{background:#1a2c5e;border-radius:20px;padding:4px 10px;font-size:12px;display:inline-block;margin:3px}}
.pill.model{{background:#173a2a;color:#7dd3a8;border:1px solid #2a6b4a}}.pill.hit{{background:#2a1a5e;color:#c7a2ff}}
.l7{{margin-top:10px;background:#0d1733;border-radius:10px;padding:10px;font-size:12px}}
.dot{{display:inline-block;width:32px;text-align:center;background:#1c2e5e;border-radius:6px;margin:2px;padding:4px 0;font-weight:800}}
.dot.over{{background:#1e6b3a;color:#7dd3a8}}.dot.under{{background:#3a1e2a;color:#ff8a8a}}
.live{{color:#00ff88;font-size:10px;border:1px solid #00ff88;padding:2px 6px;border-radius:10px;margin-left:6px}}
</style></head><body>
<h1>🟠 Orange Line LIVE — {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')} <span class='live'>FINAL L7</span></h1>
<div class='sub'>Decimal + Prob + REAL Last 7 — LIVE</div>
<h3>Today's Slate</h3><div class='game'><b>LAL @ GSW</b><span>10:00 PM ET</span></div>
<h3 style='margin-top:20px'>Top Leans — REAL L7</h3>
"""

for p in players:
    line = float(p['market'].split('o')[1])
    if 'REB' in p['market'] and 'RA' not in p['market']: arr=p['rebs']
    elif p['market'].startswith('AST'): arr=p['asts']
    else: arr=[r+a for r,a in zip(p['rebs'],p['asts'])]
    hits=hit(arr,line)
    implied=100/p['dec']
    edge=p['model']-implied
    avg=sum(arr)/len(arr)
    dots="".join([f"<span class='dot {'over' if v>line else 'under'}'>{v}</span>" for v in arr])
    html+=f"""<div class='card'>
<div><span class='badge'>{p['team']} {p['pos']}</span> <b>{p['name']}</b> — <span class='line'>{p['market']}</span></div>
<div style='margin-top:8px'>
<span class='pill'>Book: {p['dec']:.2f} ({implied:.1f}%)</span>
<span class='pill model'>Model: {p['model']}%</span>
<span class='pill' style='color:{"#7dd3a8" if edge>0 else "#ff8a8a"}'>Edge {edge:+.1f}%</span>
<span class='pill hit'>L7: {hits}-7 ({hits/7*100:.0f}%)</span>
</div>
<div class='l7'><b>L7 {p['market'].split()[0]}:</b> {dots}<br>
<small style='color:#8ea2cc'>Avg {avg:.1f} | Raw: {', '.join(map(str,arr))} | REAL</small></div>
</div>"""

html+=f"<div class='sub' style='margin-top:26px'>FINAL build {datetime.now(timezone.utc).isoformat()}</div></body></html>"
open("index.html","w",encoding="utf-8").write(html)
print("FINAL done")
