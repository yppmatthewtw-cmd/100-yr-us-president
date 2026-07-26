# -*- coding: utf-8 -*-
"""R4 — 美國總統E-H MONEY R4 (MM-DD_hkHH.MM).html

把 Easy/Hard 指數與判區改用附件的三引擎整合 (A∩B∩C) 共識重新排列。

PANE 1  現任真實時間軸（月份刻度）× Easy/Hard 指數，疊上 25 屆前任作對比，現屆 highlight
PANE 3  全 26 屆壓縮堆疊（同一時間軸、一頁看完），現屆 highlight；可逐屆展開
PANE 2  同位對照（置於頁面最下方）
"""
import os, json, html, glob, datetime as dt
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
S=os.path.join(ROOT,"data")
CSS=open(os.path.join(ROOT,"assets","style.css")).read()
JS =open(os.path.join(ROOT,"assets","r5_engine.js")).read()
A  =json.load(open(f"{S}/anchor_r5.json"))

def esc(x): return html.escape(str(x)) if x is not None else ""
AN=A["anchor"]; TERMS=A["terms"]
nA=sum(1 for t in TERMS if t["tier"]=="A"); nB=sum(1 for t in TERMS if t["tier"]=="B")
ntr=sum(len(t["transitions"]) for t in TERMS)
CUR=[t for t in TERMS if t["name"]==AN["name"]][0]

HK=dt.datetime.now(dt.timezone(dt.timedelta(hours=8)))
STAMP=f"{HK:%m-%d}_hk{HK:%H.%M}"
FNAME=f"美國總統E-H MONEY R5 ({STAMP}).html"
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

engine_rows=""
for k,v in A["engines"].items():
    cur=" class='eng-cur'" if k.startswith("整合") else ""
    engine_rows+=(f"<tr{cur}><td>{esc(k)}</td>"
                  f"<td class='mono'>{v['EASY']}%</td><td class='mono'>{v['UNCERTAIN']}%</td>"
                  f"<td class='mono'>{v['HARD']}%</td></tr>")

DATA_JSON=json.dumps({"anchor":A}, separators=(',',':'), ensure_ascii=False)

HTML=f"""<!doctype html>
<html lang="zh-Hant"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>美國總統 E/H MONEY R5 — 三引擎整合 A∩B∩C（{STAMP}）</title>
<style>{CSS}</style>
</head><body>
<button class="theme-btn" id="theme-btn" type="button">☀️ 淺色模式</button>
<header class="hero">
  <div class="hero-eyebrow">R5 · 三引擎整合 A∩B∩C · 現任錨定 · 生成 {esc(HK.strftime('%Y-%m-%d %H:%M'))} 香港時間</div>
  <h1>美國總統 E/H MONEY <span class="hero-r1">R5</span></h1>
  <div class="hero-sub"><b>Easy/Hard 指數與判區已改用三引擎整合（A∩B∩C）共識重新排列</b>：
  三個引擎（A Fable 18項／B Sol 5項／C Grok 18項）同日全部 EASY 才判 EASY、全部 HARD 才判 HARD，
  其餘一律 UNCERTAIN。X 軸＝<b>現任總統（特朗普 II）的真實日曆</b>，逐月標刻：
  <b>YEAR 0</b> 當選 2024-11 → <b>YEAR 1</b> 就職 2025-01-20 → <b>YEAR 2</b> 2026 →
  <b>YEAR 3</b> 2027 → <b>YEAR 4</b> 2028 → <b>YEAR 5</b> 卸任 2029-01-20。
  歷任 25 屆按就任週期日對齊到同一條軸，<b>PANE 1 與 PANE 3 都把全部總統放在同一張圖對比，並把現屆狀態 highlight</b>。</div>
  <div class="hero-strip">
    <span class="hs easy">整合 EASY {A['engines']['整合 A∩B∩C']['EASY']}% · UNC {A['engines']['整合 A∩B∩C']['UNCERTAIN']}% · HARD {A['engines']['整合 A∩B∩C']['HARD']}%</span>
    <span class="hs unc">現在 {esc(AN['now'])} · 週期第 {AN['cd_now']} 日 · {zn(cur_at['z'])} {cur_at['v']:.0f}</span>
    <span class="hs hard">{ntr} 次轉區全部注記 · 距中期選舉 {DAYS_TO_MID} 日</span>
  </div>
</header>

<nav class="toc">
  <a href="#engines">整合規則</a><a href="#pane1">PANE 1 現任主圖</a>
  <a href="#pane3">PANE 3 全 26 屆壓縮對照</a><a href="#pane2">PANE 2 同位對照</a>
</nav>

<section id="engines" class="block">
  <h2>整合規則與三引擎對照（2016-07 → 2026-07，{A['n_days']} 個交易日）</h2>
  <p class="muted">整合判區＝<b>三票全同才算數</b>：三引擎同日全部 EASY → EASY；全部 HARD → HARD；
  任何一個唱反調 → UNCERTAIN。因三者門檻與指標數不同（A ≥70/≤40 共18項；B ≥92/&lt;45 共5項；C ≥80/&lt;40 共18項），
  整合後 EASY 由 A 單獨的 69.9% 收窄至 {A['engines']['整合 A∩B∩C']['EASY']}%。</p>
  <div class="pm-wrap"><table class="cs eng-tbl" style="max-width:640px">
    <thead><tr><th>引擎</th><th>EASY</th><th>UNCERTAIN</th><th>HARD</th></tr></thead>
    <tbody>{engine_rows}</tbody></table></div>
  <div class="warn-box">
    <h4>⚠ 跨層比較須知（重要）</h4>
    <p>整合指數只存在於 <b>2016-07 之後</b>（4 屆量測級）。<b>2016 年前的 22 屆沒有 A/B/C 資料，無法重算</b>，
    仍沿用 R1 窗口重建的分段——而該重建是以<b>寬鬆的 A 引擎</b>為校準基準（A 判 69.9% 的日子為 EASY），
    整合標準只判 {A['engines']['整合 A∩B∩C']['EASY']}%。因此<b>不可直接橫向比較兩層的 EASY 佔比</b>：
    量測級看起來「綠色少很多」是引擎口徑差異，不是歷史差異。每列右側已標示所用標準
    （<span class="std-tag std-c">整合 A∩B∩C</span> / <span class="std-tag std-r">重建（A 校準）</span>）。
    可靠的跨層比較是 <b>HARD 段的位置</b>——整合標準下的四次 HARD（2018Q4、2020 COVID、2022 熊市、2025 關稅）
    與 A 引擎完全對上，時點一致。</p>
  </div>
  <p class="muted">三引擎兩兩一致度：A–B 40.3%、A–C 48.7%、B–C 74.0%；三方完全一致僅 32.1%。
  平均分歧度（三引擎標準化分數 max−min）＝ {A['avg_spread']}。分歧本身即訊號：分歧越大代表制度越不明朗。</p>
</section>

<!-- ==================== PANE 1 ==================== -->
<section id="pane1" class="block">
  <div class="pane-tag">PANE 1</div>
  <div class="cy-block">
    <div class="cy-head"><div>
      <h2 class="cy-h2">★ 現任（特朗普 II）— 真實時間軸 × Easy/Hard 指數 × 轉區注記</h2>
      <p class="cy-sub"><b style="color:var(--head)">粗線＝現屆整合指數</b>（A∩B∩C 共識，21 日平滑）；
      細藍/橙/紫線＝A/B/C 三引擎各自的標準化分數（門檻已對齊到 40/70）；
      背景灰線＝<b>其餘 25 屆前任</b>按同一週期位置疊上作對比；
      黃虛線＝26 屆中位數；下方色帶＝現屆制度級資金區，帶編號圓點＝每次轉區（停留看主因與事件）；
      <b style="color:#7fd4ff">藍色直線＝現在</b>。X 軸每個年份都標到月份。</p>
    </div>
    <div class="cy-controls"><button class="cy-btn on" id="p1-engines" type="button">☑ 顯示 A/B/C 三引擎分線</button></div>
    </div>
    <div class="cy-chart am-master-wrap" id="p1-chart"></div>
    <div class="p1-legend">
      <span><i style="background:var(--chart-hi);height:3px"></i>現屆（highlight）</span>
      <span><i style="background:#7f93b3;opacity:.5"></i>其餘 25 屆前任</span>
      <span><i style="background:#3987e5"></i>A Fable</span>
      <span><i style="background:#d95926"></i>B Sol</span>
      <span><i style="background:#9085e9"></i>C Grok</span>
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

  <h3 class="blk">逐任總統比較（展開任一位即在上圖疊上其軌跡，並列出促使其離開 EASY 的重大事件）</h3>
  <div class="am-controls">
    <button class="cy-btn" id="p1-expand" type="button">▼ 展開前 6 位</button>
    <button class="cy-btn" id="p1-collapse" type="button">▲ 全部收合</button>
    <span class="muted" style="font-size:11.5px">展開後該任期會以專屬顏色畫在 PANE 1 圖上，▼ 標記＝離開 EASY 的時點</span>
  </div>
  <div class="p1-list" id="p1-list"></div>
</section>

<!-- ==================== PANE 3 ==================== -->
<section id="pane3" class="block">
  <div class="pane-tag p3">PANE 3</div>
  <h2>歷任 26 屆 — 同一時間軸壓縮對照（一頁看完）＋逐屆展開/收合</h2>
  <p class="muted"><b>每條 bar 上已寫上該任期內 Fed 開始加息（▲橙）／開始減息（▼青）的時點。</b>
  <b style="color:var(--unc)">注意：左側色條標示所用標準</b>——
  <span style="color:#7fd4ff">藍＝整合 A∩B∩C</span>（頂部 4 屆）、灰＝重建（A 校準）（其餘 22 屆）。
  兩者口徑不同，橫向比較請只看 <b>HARD 段位置</b>，不要比 EASY 佔比。
  全部 26 屆用<b>與 PANE 1 完全相同的年份/月份時間節點</b>壓縮成一頁：
  每列一屆（新→舊），顏色＝資金區，右側方塊＝該屆走到「現在這個週期位置」時的區與指數，
  列下三角＝任內大底（黃＝落在第2年中期選舉年）。<b style="color:#7fd4ff">藍框列＝現屆</b>。
  點左側名稱可跳到該屆的展開明細。</p>
  <div class="p3-stack-wrap" id="p3-stack"></div>
  <div class="p3-legend">
    <span><i style="background:#2e9b6f"></i>EASY</span>
    <span><i style="background:#c99a2e"></i>UNCERTAIN</span>
    <span><i style="background:#d2566c"></i>HARD</span>
    <span><i style="background:#7fd4ff"></i>整合 A∩B∩C 標準（4 屆量測級）</span>
    <span><i style="background:#4a5a72"></i>重建（A 校準）標準（22 屆）— 口徑不同，不可直接比 EASY 佔比</span>
    <span>▾ 任內大底（<span style="color:#ffd479">黃＝第2年中期選舉年</span>）</span>
  </div>
  <div class="fed-legend">
    <span><b style="color:#ff8f6b">▲ 開始加息</b>（每格條上方橙色三角＋日期）</span>
    <span><b style="color:#63e6c3">▼ 開始減息</b>（條下方青色三角＋日期）</span>
    <span class="muted">共 49 個百年 Fed 政策轉折點，投影到各任期的對應週期位置；滑鼠停留看該次轉折的說明</span>
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
  <p>版本：R5（三引擎整合 A∩B∩C · 現任錨定 · 月份刻度 · 三 PANE）· 生成 {esc(HK.strftime('%Y-%m-%d %H:%M'))} 香港時間 · 檔名 {esc(FNAME)}</p>
  <p>資料來源：EasyHardMoney_NDX_2026R4.5.3_COMBINED_ABC（01_整合判區，A∩B∩C 三引擎共識，量測級 {nA} 屆每日判區）；
  美國總統任期百年 EasyHard 資金市場週期 R1（重建級 {nB} 屆逐屆窗口）。
  轉區原因：量測級取經核實的分段驅動＋事件庫，重建級取 R1 逐段依據注記；{ntr} 次轉區全部有注記。</p>
  <p class="disclaim">1937 年前就職日為 3 月 4 日，對齊以各自就職日為第 0 日，與日曆年帶有約 6 週漂移。
  現屆「未來」段（現在→卸任）留白，不作預測。本報告為市場史/框架研究，非投資建議。</p>
</footer>

<script>const DATA={DATA_JSON};{JS}</script>
</body></html>"""

for f in glob.glob(os.path.join(ROOT,"美國總統E-H MONEY R5 (*).html")): os.remove(f)
out=os.path.join(ROOT,FNAME)
open(out,"w").write(HTML)
print("written:",FNAME,f"({len(HTML)} bytes)")
