# -*- coding: utf-8 -*-
"""R3 — 美國總統E-H MONEY R3 (MM-DD_hkHH.MM).html

PANE 1  現任真實時間軸（月份刻度）× Easy/Hard 指數，疊上 25 屆前任作對比，現屆 highlight
PANE 3  全 26 屆壓縮堆疊（同一時間軸、一頁看完），現屆 highlight；可逐屆展開
PANE 2  同位對照（置於頁面最下方）
"""
import os, json, html, glob, datetime as dt
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
S=os.path.join(ROOT,"data")
CSS=open(os.path.join(ROOT,"assets","style.css")).read()
JS =open(os.path.join(ROOT,"assets","r3_engine.js")).read()
A  =json.load(open(f"{S}/anchor.json"))

def esc(x): return html.escape(str(x)) if x is not None else ""
AN=A["anchor"]; TERMS=A["terms"]
nA=sum(1 for t in TERMS if t["tier"]=="A"); nB=sum(1 for t in TERMS if t["tier"]=="B")
ntr=sum(len(t["transitions"]) for t in TERMS)
CUR=[t for t in TERMS if t["name"]==AN["name"]][0]

HK=dt.datetime.now(dt.timezone(dt.timedelta(hours=8)))
STAMP=f"{HK:%m-%d}_hk{HK:%H.%M}"
FNAME=f"美國總統E-H MONEY R3 ({STAMP}).html"
DAYS_TO_MID=(dt.date(2026,11,3)-dt.date.fromisoformat(AN["now"])).days

def zn(z): return {"E":"EASY","U":"UNCERTAIN","H":"HARD"}[z]
def zcls(z): return {"E":"easy","U":"unc","H":"hard"}[z]

# PANE 2 rows (newest first), current president pinned on top
rows=""
cur_at=CUR["at_now"]
for t in reversed(TERMS):
    if not t["at_now"]: continue
    z=t["at_now"]["z"]; isc=(t["name"]==AN["name"])
    same = (cur_at and z==cur_at["z"])
    rows+=(f"<tr class='{'p2-cur' if isc else ''}'>"
           f"<td class='am-nowp'>{'<span class=cur-tag>現任</span> ' if isc else ''}{esc(t['cn'])}"
           f"<small class='p2-yr'>{esc(t['inaug'][:4])}–{esc(t['end'][:4])}</small></td>"
           f"<td class='mono'>{esc(t['at_now']['own'])}</td>"
           f"<td><span class='zbadge {zcls(z)}'>{zn(z)}</span></td>"
           f"<td class='mono'>{t['at_now']['v']:.0f}</td>"
           f"<td class='mono p2-same'>{'●' if (same and not isc) else ''}</td></tr>")
n_same=sum(1 for t in TERMS if t["at_now"] and cur_at and t["at_now"]["z"]==cur_at["z"] and t["name"]!=AN["name"])
n_hard=sum(1 for t in TERMS if t["at_now"] and t["at_now"]["z"]=="H")
n_tot=sum(1 for t in TERMS if t["at_now"])

DATA_JSON=json.dumps({"anchor":A}, separators=(',',':'), ensure_ascii=False)

HTML=f"""<!doctype html>
<html lang="zh-Hant"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>美國總統 E/H MONEY R3 — 現任真實時間軸對標歷任（{STAMP}）</title>
<style>{CSS}</style>
</head><body>
<header class="hero">
  <div class="hero-eyebrow">R3 · 現任錨定 · 月份刻度 · 生成 {esc(HK.strftime('%Y-%m-%d %H:%M'))} 香港時間</div>
  <h1>美國總統 E/H MONEY <span class="hero-r1">R3</span></h1>
  <div class="hero-sub">X 軸＝<b>現任總統（特朗普 II）的真實日曆</b>，逐月標刻：
  <b>YEAR 0</b> 當選 2024-11 → <b>YEAR 1</b> 就職 2025-01-20 → <b>YEAR 2</b> 2026 →
  <b>YEAR 3</b> 2027 → <b>YEAR 4</b> 2028 → <b>YEAR 5</b> 卸任 2029-01-20。
  歷任 25 屆按就任週期日對齊到同一條軸，<b>PANE 1 與 PANE 3 都把全部總統放在同一張圖對比，並把現屆狀態 highlight</b>。</div>
  <div class="hero-strip">
    <span class="hs easy">26 屆 · {ntr} 次轉區全部注記</span>
    <span class="hs unc">現在 {esc(AN['now'])} · 週期第 {AN['cd_now']} 日 · {zn(cur_at['z'])} {cur_at['v']:.0f}</span>
    <span class="hs hard">距中期選舉 {DAYS_TO_MID} 日</span>
  </div>
</header>

<nav class="toc">
  <a href="#pane1">PANE 1 現任主圖</a><a href="#pane3">PANE 3 全 26 屆壓縮對照</a><a href="#pane2">PANE 2 同位對照</a>
</nav>

<!-- ==================== PANE 1 ==================== -->
<section id="pane1" class="block">
  <div class="pane-tag">PANE 1</div>
  <div class="cy-block">
    <div class="cy-head"><div>
      <h2 class="cy-h2">★ 現任（特朗普 II）— 真實時間軸 × Easy/Hard 指數 × 轉區注記</h2>
      <p class="cy-sub"><b style="color:#fff">粗白線＝現屆</b>（每日 18 指標合成分，21 日平滑）；
      背景灰線＝<b>其餘 25 屆前任</b>按同一週期位置疊上作對比；
      黃虛線＝26 屆中位數；下方色帶＝現屆制度級資金區，帶編號圓點＝每次轉區（停留看主因與事件）；
      <b style="color:#7fd4ff">藍色直線＝現在</b>。X 軸每個年份都標到月份。</p>
    </div></div>
    <div class="cy-chart am-master-wrap" id="p1-chart"></div>
    <div class="p1-legend">
      <span><i style="background:#fff;height:3px"></i>現屆（highlight）</span>
      <span><i style="background:#7f93b3;opacity:.5"></i>其餘 25 屆前任</span>
      <span><i style="background:#ffd479"></i>26 屆中位數</span>
      <span><i style="background:#2e9b6f"></i>EASY</span>
      <span><i style="background:#c99a2e"></i>UNCERTAIN</span>
      <span><i style="background:#d2566c"></i>HARD</span>
      <span><i style="background:#7fd4ff"></i>現在 {esc(AN['now'])}</span>
    </div>
    <div class="cy-foot">現在＝週期第 {AN['cd_now']} 日＝YEAR 2（中期選舉年）中後段，距 2026-11-03 中期選舉 {DAYS_TO_MID} 日。
    百年劇本：第2年 Hard 高發段的大底多落 Q4，其後 YEAR 3（2027）為全週期最強一段。</div>
    <h3 class="blk">現屆轉區明細</h3>
    <div id="p1-tt"></div>
  </div>
</section>

<!-- ==================== PANE 3 ==================== -->
<section id="pane3" class="block">
  <div class="pane-tag p3">PANE 3</div>
  <h2>歷任 26 屆 — 同一時間軸壓縮對照（一頁看完）＋逐屆展開/收合</h2>
  <p class="muted">全部 26 屆用<b>與 PANE 1 完全相同的年份/月份時間節點</b>壓縮成一頁：
  每列一屆（新→舊），顏色＝資金區，右側方塊＝該屆走到「現在這個週期位置」時的區與指數，
  列下三角＝任內大底（黃＝落在第2年中期選舉年）。<b style="color:#7fd4ff">藍框列＝現屆</b>。
  點左側名稱可跳到該屆的展開明細。</p>
  <div class="p3-stack-wrap" id="p3-stack"></div>
  <div class="p3-legend">
    <span><i style="background:#2e9b6f"></i>EASY</span>
    <span><i style="background:#c99a2e"></i>UNCERTAIN</span>
    <span><i style="background:#d2566c"></i>HARD</span>
    <span><i style="background:#3ecf8e"></i>量測級 A（每日18指標）</span>
    <span><i style="background:#4a5a72"></i>重建級 B（R1窗口+市場史）</span>
    <span>▾ 任內大底（<span style="color:#ffd479">黃＝第2年中期選舉年</span>）</span>
  </div>
  <h3 class="blk">逐屆展開明細（每屆可獨立展開/收合）</h3>
  <div class="am-controls">
    <button class="cy-btn" id="p3-expand" type="button">▼ 全部展開</button>
    <button class="cy-btn" id="p3-collapse" type="button">▲ 全部收合</button>
    <span class="muted" style="font-size:11.5px">展開後顯示該屆對標現任時間軸的完整分段、編號轉區旗標與「主因＋大事件」明細</span>
  </div>
  <div id="p3-cards"></div>
</section>

<!-- ==================== PANE 2 (bottom) ==================== -->
<section id="pane2" class="block">
  <div class="pane-tag p2">PANE 2</div>
  <h2>同位對照：歷任走到「現在這個位置」（週期第 {AN['cd_now']} 日）時正處什麼區？</h2>
  <p class="muted">把現在（{esc(AN['now'])}，就任後第 {AN['cd_now']} 日）對映到每位前任自己的日曆。
  現屆為 <b class="t{cur_at['z']}">{zn(cur_at['z'])} {cur_at['v']:.0f}</b>；
  {n_tot} 屆之中有 <b>{n_same} 屆</b>在同一週期位置同樣處於 {zn(cur_at['z'])}（右欄 ● 標示），
  <b>{n_hard} 屆</b>處於 HARD。</p>
  <div class="pm-wrap"><table class="kd p2-tt" style="max-width:700px">
    <thead><tr><th>總統</th><th>自家同位日期</th><th>當時資金區</th><th>指數</th><th>同區</th></tr></thead>
    <tbody>{rows}</tbody></table></div>
</section>

<footer class="foot">
  <p>版本：R3（現任錨定 · 月份刻度 · 三 PANE）· 生成 {esc(HK.strftime('%Y-%m-%d %H:%M'))} 香港時間 · 檔名 {esc(FNAME)}</p>
  <p>資料來源：A-(Fable) EasyHardMoney 三區指標庫及 NDX 十年每日分段 2026R4.5.3_2（量測級 {nA} 屆每日判區）；
  美國總統任期百年 EasyHard 資金市場週期 R1（重建級 {nB} 屆逐屆窗口）。
  轉區原因：量測級取經核實的分段驅動＋事件庫，重建級取 R1 逐段依據注記；{ntr} 次轉區全部有注記。</p>
  <p class="disclaim">1937 年前就職日為 3 月 4 日，對齊以各自就職日為第 0 日，與日曆年帶有約 6 週漂移。
  現屆「未來」段（現在→卸任）留白，不作預測。本報告為市場史/框架研究，非投資建議。</p>
</footer>

<script>const DATA={DATA_JSON};{JS}</script>
</body></html>"""

for f in glob.glob(os.path.join(ROOT,"美國總統E-H MONEY R3 (*).html")): os.remove(f)
out=os.path.join(ROOT,FNAME)
open(out,"w").write(HTML)
print("written:",FNAME,f"({len(HTML)} bytes)")
