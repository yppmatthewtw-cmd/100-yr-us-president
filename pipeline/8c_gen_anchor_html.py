# -*- coding: utf-8 -*-
"""R2 (現任錨定版) — generate 「美國總統E-H MONEY R2 (MM-DD_hkHH.MM).html」.

X axis = the current president's REAL calendar (YEAR 0 election 2024-11 →
YEAR 5 end of term 2029-01-20); every predecessor projected onto it; every
zone transition annotated; every president individually expand/collapse.
Filename carries the Hong Kong generation timestamp. ("/" is illegal in
filenames, so E/H is written E-H.)
"""
import os, json, html, glob, datetime as dt
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
S=os.path.join(ROOT,"data")
CSS=open(os.path.join(ROOT,"assets","style.css")).read()
JS =open(os.path.join(ROOT,"assets","anchor_engine.js")).read()
A  =json.load(open(f"{S}/anchor.json"))

def esc(x): return html.escape(str(x)) if x is not None else ""
AN=A["anchor"]; TERMS=A["terms"]
nA=sum(1 for t in TERMS if t["tier"]=="A"); nB=sum(1 for t in TERMS if t["tier"]=="B")
ntr=sum(len(t["transitions"]) for t in TERMS)

HK=dt.datetime.now(dt.timezone(dt.timedelta(hours=8)))
STAMP=f"{HK:%m-%d}_hk{HK:%H.%M}"
FNAME=f"美國總統E-H MONEY R2 ({STAMP}).html"

# at-now comparison strip data (for the summary box)
def zn(z): return {"E":"EASY","U":"UNCERTAIN","H":"HARD"}[z]
now_rows=""
for t in reversed(TERMS):
    if not t["at_now"]: continue
    z=t["at_now"]["z"]
    cls={"E":"easy","U":"unc","H":"hard"}[z]
    now_rows+=(f"<tr><td class='am-nowp'>{esc(t['cn'])}</td>"
               f"<td class='mono'>{esc(t['at_now']['own'])}</td>"
               f"<td><span class='zbadge {cls}'>{zn(z)}</span></td>"
               f"<td class='mono'>{t['at_now']['v']:.0f}</td></tr>")

DATA_JSON=json.dumps({"anchor":A}, separators=(',',':'), ensure_ascii=False)

HTML=f"""<!doctype html>
<html lang="zh-Hant"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>美國總統 E/H MONEY R2 — 現任真實時間軸對標歷任（{STAMP}）</title>
<style>{CSS}</style>
</head><body>
<header class="hero">
  <div class="hero-eyebrow">R2 · 現任錨定 · 生成 {esc(HK.strftime('%Y-%m-%d %H:%M'))} 香港時間</div>
  <h1>美國總統 E/H MONEY <span class="hero-r1">R2</span></h1>
  <div class="hero-sub">以<b>現任總統（特朗普 II）的真實日曆時間</b>作為 X 軸：
  <b>YEAR 0</b> 當選（2024年11月）→ <b>YEAR 1</b> 就職（2025-01-20）→ <b>YEAR 2</b>（2026）→
  <b>YEAR 3</b>（2027）→ <b>YEAR 4</b>（2028）→ <b>YEAR 5</b> 卸任（2029-01-20）。
  歷任 25 屆前總統全部按「就任週期日」對齊到同一條軸上——在現任的任何一個日子，
  都可直接讀出每位前任「當年走到同一位置時」正處什麼資金區、以及他們每一次轉區的原因與大事件。</div>
  <div class="hero-strip">
    <span class="hs easy">26 屆 · {ntr} 次轉區全部標注原因</span>
    <span class="hs unc">藍線＝現在 {esc(AN['now'])}（週期第 {AN['cd_now']} 日）</span>
    <span class="hs hard">{nA} 屆量測級 · {nB} 屆重建級</span>
  </div>
</header>

<nav class="toc">
  <a href="#master">★現任主圖</a><a href="#atnow">同位對照</a><a href="#cards">歷任逐屆（展開/收合）</a>
</nav>

<section id="master" class="block">
  <div class="cy-block">
    <div class="cy-head"><div>
      <h2 class="cy-h2">★ 現任（特朗普 II）— 真實時間軸 × Easy/Hard 指數 × 轉區注記</h2>
      <p class="cy-sub">白線＝每日 18 指標合成分（21 日平滑，量測級）；下方色帶＝制度級資金區分段；
      帶編號的圓點＝每次轉區（滑鼠停留看原因與事件，完整明細見下表）；<b style="color:#7fd4ff">藍色直線＝現在</b>。</p>
    </div></div>
    <div class="cy-chart am-master-wrap" id="am-master"></div>
    <div class="cy-foot">現在位置：週期第 {AN['cd_now']} 日＝YEAR 2（中期選舉年）中後段，距 2026-11-03 中期選舉約 {(dt.date(2026,11,3)-dt.date.fromisoformat(AN['now'])).days} 日。
    百年劇本：第2年 Hard 高發段的大底多落 Q4（見 R2 百年版），其後第3年（2027）為全週期最強一段。</div>
    <h3 class="blk">現任轉區明細</h3>
    <div id="am-master-tt"></div>
  </div>
</section>

<section id="atnow" class="block">
  <h2>同位對照：歷任走到「現在這個位置」（週期第 {AN['cd_now']} 日）時正處什麼區？</h2>
  <p class="muted">把現在（{esc(AN['now'])}，就任後第 {AN['cd_now']} 日）對映到每位前任自己的日曆——
  例如拜登的同位日是 2022-07-09（加息熊市最深處），特朗普 I 的同位日是 2018-07-09（貿易戰夏季仍 EASY）。</p>
  <div class="pm-wrap"><table class="kd" style="max-width:640px">
    <thead><tr><th>總統</th><th>自家同位日期</th><th>當時資金區</th><th>指數</th></tr></thead>
    <tbody>{now_rows}</tbody></table></div>
</section>

<section id="cards" class="block">
  <h2>歷任 25 屆 — 逐屆展開/收合比較（新→舊）</h2>
  <p class="muted">每列可獨立展開：展開後顯示該屆對標現任時間軸的完整分段、
  每次轉區的編號旗標與「主因＋大事件」明細表（自家日期 ↔ 對標現任日期並列）。
  摘要列右側為「同位」晶片＝該屆在現在這個週期位置時的資金區。</p>
  <div class="am-controls">
    <button class="cy-btn" id="am-expand-all" type="button">▼ 全部展開</button>
    <button class="cy-btn" id="am-collapse-all" type="button">▲ 全部收合</button>
    <span class="muted" style="font-size:11.5px">▾ 白/黃三角＝任內大底（黃＝落在第2年中期選舉年）；量測級(A)＝每日18指標；重建級(B)＝R1窗口+市場史</span>
  </div>
  <div id="am-cards"></div>
</section>

<footer class="foot">
  <p>版本：R2（現任錨定版）· 生成 {esc(HK.strftime('%Y-%m-%d %H:%M'))} 香港時間 · 檔名 {esc(FNAME)}</p>
  <p>資料來源：A-(Fable) EasyHardMoney 三區指標庫及 NDX 十年每日分段 2026R4.5.3_2（量測級每日判區）；
  美國總統任期百年 EasyHard 資金市場週期 R1（重建級逐屆窗口）。轉區原因：量測級取經核實的分段驅動與事件庫，重建級取 R1 逐段依據注記。</p>
  <p class="disclaim">1937 年前就職日為 3 月 4 日，對齊以就職日為第 0 日，與日曆年帶有約 6 週漂移。本報告為市場史/框架研究，非投資建議。</p>
</footer>

<script>const DATA={DATA_JSON};{JS}</script>
</body></html>"""

# remove previous timestamped versions, then write the new one
for f in glob.glob(os.path.join(ROOT,"美國總統E-H MONEY R2 (*).html")):
    os.remove(f)
out=os.path.join(ROOT,FNAME)
open(out,"w").write(HTML)
print("written:",FNAME,f"({len(HTML)} bytes)")
