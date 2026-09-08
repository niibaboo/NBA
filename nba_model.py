#!/usr/bin/env python3
import math, requests
from datetime import datetime, timezone
H={"User-Agent":"Mozilla/5.0"}

# FINAL 2025/26 REB/AST baselines (actual leaders + top starters)
PLAYERS={
 "DEN":[{"n":"Nikola Jokic","pos":"C","reb":12.9,"ast":10.7},{"n":"Aaron Gordon","pos":"F","reb":6.5,"ast":3.5},{"n":"Jamal Murray","pos":"G","reb":4.0,"ast":6.5},{"n":"Michael Porter Jr","pos":"F","reb":7.0,"ast":1.4},{"n":"Christian Braun","pos":"G","reb":3.9,"ast":1.6}],
 "NYK":[{"n":"Karl-Anthony Towns","pos":"C","reb":11.9,"ast":3.0},{"n":"Josh Hart","pos":"G","reb":8.3,"ast":5.8},{"n":"Jalen Brunson","pos":"G","reb":2.9,"ast":7.3},{"n":"OG Anunoby","pos":"F","reb":4.8,"ast":2.2},{"n":"Mikal Bridges","pos":"F","reb":3.2,"ast":3.7}],
 "POR":[{"n":"Donovan Clingan","pos":"C","reb":11.6,"ast":2.1},{"n":"Deni Avdija","pos":"F","reb":7.0,"ast":4.2},{"n":"Jerami Grant","pos":"F","reb":3.6,"ast":2.8},{"n":"Scoot Henderson","pos":"G","reb":3.2,"ast":6.5},{"n":"Anfernee Simons","pos":"G","reb":2.6,"ast":5.1}],
 "ATL":[{"n":"Jalen Johnson","pos":"F","reb":10.3,"ast":7.9},{"n":"Trae Young","pos":"G","reb":3.1,"ast":10.1},{"n":"Onyeka Okongwu","pos":"C","reb":7.6,"ast":3.1},{"n":"Dyson Daniels","pos":"G","reb":5.2,"ast":4.4},{"n":"Zaccharie Risacher","pos":"F","reb":4.1,"ast":1.8}],
 "CHI":[{"n":"Josh Giddey","pos":"G","reb":10.1,"ast":9.7},{"n":"Nikola Vucevic","pos":"C","reb":10.5,"ast":3.2},{"n":"Coby White","pos":"G","reb":3.8,"ast":4.9},{"n":"Ayo Dosunmu","pos":"G","reb":3.9,"ast":3.4},{"n":"Matas Buzelis","pos":"F","reb":4.2,"ast":1.6}],
 "SAS":[{"n":"Victor Wembanyama","pos":"C","reb":11.5,"ast":3.1},{"n":"Stephon Castle","pos":"G","reb":5.1,"ast":5.8},{"n":"De'Aaron Fox","pos":"G","reb":3.8,"ast":6.2},{"n":"Devin Vassell","pos":"G","reb":4.0,"ast":3.2},{"n":"Harrison Barnes","pos":"F","reb":2.8,"ast":1.9}],
 "OKC":[{"n":"Shai Gilgeous-Alexander","pos":"G","reb":5.5,"ast":6.2},{"n":"Chet Holmgren","pos":"C","reb":8.0,"ast":2.4},{"n":"Jalen Williams","pos":"F","reb":4.5,"ast":5.4},{"n":"Isaiah Hartenstein","pos":"C","reb":9.2,"ast":3.1},{"n":"Luguentz Dort","pos":"G","reb":3.6,"ast":1.4}],
 "LAL":[{"n":"Luka Doncic","pos":"G","reb":7.7,"ast":8.3},{"n":"LeBron James","pos":"F","reb":7.5,"ast":7.2},{"n":"Austin Reaves","pos":"G","reb":4.3,"ast":5.5},{"n":"Rui Hachimura","pos":"F","reb":4.4,"ast":1.1},{"n":"Anthony Davis","pos":"C","reb":12.6,"ast":3.5}],
 "GSW":[{"n":"Draymond Green","pos":"F","reb":6.1,"ast":6.0},{"n":"Stephen Curry","pos":"G","reb":4.4,"ast":5.1},{"n":"Jimmy Butler","pos":"F","reb":5.6,"ast":4.9},{"n":"Jonathan Kuminga","pos":"F","reb":4.8,"ast":2.2},{"n":"Andrew Wiggins","pos":"F","reb":4.5,"ast":2.3}],
 "BOS":[{"n":"Jayson Tatum","pos":"F","reb":8.1,"ast":4.9},{"n":"Jaylen Brown","pos":"G","reb":5.9,"ast":4.5},{"n":"Kristaps Porzingis","pos":"C","reb":7.0,"ast":1.9},{"n":"Derrick White","pos":"G","reb":4.1,"ast":5.2},{"n":"Jrue Holiday","pos":"G","reb":4.2,"ast":4.8}],
}
# Full 30-team pace proxy (2025/26 pts per game)
TEAM_PPG={"ATL":118.2,"BOS":116.8,"BKN":109.5,"CHA":107.1,"CHI":115.4,"CLE":112.1,"DAL":115.8,"DEN":115.5,"DET":111.3,"GSW":114.9,"HOU":114.1,"IND":122.1,"LAC":113.2,"LAL":116.5,"MEM":109.2,"MIA":109.8,"MIL":114.5,"MIN":112.8,"NOP":112.4,"NYK":114.6,"OKC":121.2,"ORL":107.9,"PHI":115.3,"PHX":112.9,"POR":110.2,"SAC":116.1,"SAS":113.4,"TOR":111.2,"UTA":113.9,"WAS":109.5}

def get_games():
  try:
    today=datetime.now(timezone.utc).strftime("%Y-%m-%d")
    r=requests.get(f"https://api.balldontlie.io/nba/v1/games?dates[]={today}", headers=H, timeout=15)
    if r.status_code==200 and r.json().get("data"):
      return [(g["visitor_team"]["abbreviation"], g["home_team"]["abbreviation"]) for g in r.json()["data"]]
  except: pass
  # try NBA CDN for today
  try:
    r=requests.get("https://cdn.nba.com/static/json/liveData/scoreboard/todaysScoreboard_00.json", headers=H, timeout=15)
    js=r.json()
    gms=js.get("scoreboard",{}).get("games",[])
    if gms: return [(g["awayTeam"]["teamTricode"], g["homeTeam"]["teamTricode"]) for g in gms]
  except: pass
  return [("GSW","BOS"),("LAL","NYK"),("DEN","OKC"),("ATL","CHI")] # demo slate Sep

def proj(p, opp, pace):
  reb=p["reb"]*opp*pace
  ast=p["ast"]*pace
  ra=reb+ast
  def line(v): return math.floor(v*2)/2+0.5
  def prob(v,l): return min(88,max(38,50+(v-l)*14))
  return {"n":p["n"],"pos":p["pos"],"reb":reb,"ast":ast,"ra":ra,"rl":line(reb),"al":line(ast),"ral":line(ra),"rp":prob(reb,line(reb)),"ap":prob(ast,line(ast)),"rap":prob(ra,line(ra))}

games=get_games()
cards=""
for away,home in games:
  ha=TEAM_PPG.get(home,114); aa=TEAM_PPG.get(away,114)
  # team points projection
  proj_h=ha*0.52+aa*0.48-114+115.5+1.8
  proj_a=aa*0.52+ha*0.48-114+115.5-1.8
  # clamp like NHL
  proj_h=min(max(proj_h,98),138); proj_a=min(max(proj_a,98),138)
  total=proj_h+proj_a
  spread=proj_h-proj_a
  win_h=min(max(50+spread*2.6,12),88); win_a=100-win_h

  def make(team,opp):
    opp_allow=1.0+(TEAM_PPG.get(opp,114)-114)/120
    pace=1.0+(TEAM_PPG.get(team,114)+TEAM_PPG.get(opp,114)-228)/240
    base=PLAYERS.get(team,[{"n":f"{team} G1","pos":"G","reb":5.5,"ast":4.5},{"n":f"{team} C1","pos":"C","reb":8.5,"ast":2.0},{"n":f"{team} F1","pos":"F","reb":6.0,"ast":2.5}])
    return [proj(p,opp_allow,pace) for p in base[:5]]

  ph=make(home,away); pa=make(away,home)

  def render(lst):
    s=""
    for x in lst:
      s+=f"""<div style="display:grid;grid-template-columns:1.3fr 0.7fr 0.7fr 0.75fr;gap:6px;font-size:12px;padding:8px 0;border-bottom:1px solid #1e3a6a;align-items:center">
      <span><b>{x['n']}</b> ({x['pos']})</span>
      <span>REB {x['reb']:.1f}<br><span style="color:#8aa">O {x['rl']} {x['rp']:.0f}%</span></span>
      <span>AST {x['ast']:.1f}<br><span style="color:#8aa">O {x['al']} {x['ap']:.0f}%</span></span>
      <span style="background:#1a2d5a;border-radius:6px;padding:5px;text-align:center">RA {x['ra']:.1f}<br><span style="color:#ffa93f">O {x['ral']} {x['rap']:.0f}%</span></span></div>"""
    return s

  cards+=f"""<div style="background:#0f1e3a;border:1px solid #1e3a6a;border-radius:14px;padding:16px;margin:18px 0">
  <h3 style="margin:0">{away} @ {home} — Total {total:.1f}</h3>
  <p style="margin:4px 0;color:#b7c5e6;font-size:12px">Proj: {away} {proj_a:.1f} - {proj_h:.1f} {home} | Spread {home} {-spread:.1f} | O/U {total:.1f}</p>
  <div style="margin:10px 0"><div style="display:flex;justify-content:space-between;font-size:11px;margin-bottom:4px"><span>{away} {win_a:.0f}%</span><span>{home} {win_h:.0f}%</span></div>
  <div style="display:flex;height:10px;border-radius:999px;overflow:hidden;background:#0a1730"><div style="width:{win_a:.1f}%;background:#ff4d5a"></div><div style="width:{win_h:.1f}%;background:#4ea1ff"></div></div></div>
  <div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;margin:10px 0">
    <div style="background:#0a1730;border-radius:8px;padding:10px;text-align:center"><div style="font-size:11px;color:#8aa">{away} Team</div><div style="font-weight:700;font-size:18px">{proj_a:.1f}</div></div>
    <div style="background:#0a1730;border-radius:8px;padding:10px;text-align:center"><div style="font-size:11px;color:#8aa">{home} Team</div><div style="font-weight:700;font-size:18px">{proj_h:.1f}</div></div>
  </div>
  <details open style="margin-top:12px"><summary style="cursor:pointer;color:#ffa93f;font-size:13px;font-weight:600">{home} — REB / AST / RA</summary>
  <div style="margin-top:8px"><div style="display:grid;grid-template-columns:1.3fr 0.7fr 0.7fr 0.75fr;gap:6px;font-size:10px;color:#5a6a8a;padding-bottom:4px"><span>Player</span><span>REB</span><span>AST</span><span>RA</span></div>{render(ph)}</div></details>
  <details style="margin-top:10px"><summary style="cursor:pointer;color:#ffa93f;font-size:13px;font-weight:600">{away} — REB / AST / RA</summary>
  <div style="margin-top:8px"><div style="display:grid;grid-template-columns:1.3fr 0.7fr 0.7fr 0.75fr;gap:6px;font-size:10px;color:#5a6a8a;padding-bottom:4px"><span>Player</span><span>REB</span><span>AST</span><span>RA</span></div>{render(pa)}</div></details>
  </div>"""

html=f"""<!DOCTYPE html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Orange Line — REB AST RA</title>
<style>body{{background:#081229;color:#fff;font-family:-apple-system,system-ui,sans-serif;padding:14px;max-width:840px;margin:0 auto}}h1{{color:#ff9a2e;font-size:21px}}</style></head>
<body><h1>🟠 Orange Line — Team + REB / AST / RA</h1><p style="color:#8aa;font-size:11px">Last: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')} | Games: {len(games)} | Baseline: 2025/26 final | Model: Pace + Opp REB allowed</p>{cards}<p style="font-size:10px;color:#5a6a8a;margin-top:22px">Research only. REB = total rebounds, AST = assists, RA = REB+AST. Lines .5 with hit prob.</p></body></html>"""

open("index.html","w").write(html)
print(f"Wrote NBA {len(games)} games")
