from datetime import datetime, timezone
html=f"""<!DOCTYPE html><html><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'><title>Orange Line</title>
<style>body{{background:#081229;color:#fff;font-family:sans-serif;padding:16px;max-width:800px;margin:0 auto}}h1{{color:#ff9a2e}}</style></head>
<body><h1>🟠 Orange Line LIVE — {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}</h1>
<p>Workflow works! Now we load full model.</p></body></html>"""
open("index.html","w").write(html)
print("Wrote index.html")
