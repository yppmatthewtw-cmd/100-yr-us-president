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
JS =open(os.path.join(ROOT,"assets","r7_engine.js")).read()
A  =json.load(open(f"{S}/anchor_r5.json"))

def esc(x): return html.escape(str(x)) if x is not None else ""
AN=A["anchor"]; TERMS=A["terms"]
nA=sum(1 for t in TERMS if t["tier"]=="A"); nB=sum(1 for t in TERMS if t["tier"]=="B")
ntr=sum(len(t["transitions"]) for t in TERMS)
CUR=[t for t in TERMS if t["name"]==AN["name"]][0]

HK=dt.datetime.now(dt.timezone(dt.timedelta(hours=8)))
STAMP=f"{HK:%m-%d}_hk{HK:%H.%M}"
FNAME=f"美國總統E-H MONEY R8 ({STAMP}).html"
DAYS_TO_MID=(dt.date(2026,11,3)-dt.date.fromisoformat(AN["now"])).days

def zn(z): return {"E":"EASY","U":"UNCERTAIN","H":"HARD"}[z]
def zcls(z): return {"E":"easy","U":"unc","H":"hard"}[z]

# PANE 2 compact chips (newest first)
cur_at=CUR["at_now"]
chips=""
for t in reversed(TERMS):
    if not t["at_now"]: continue
    z=t["at_now"]["z"]; isc=(t["name"]==AN["name"])
    same=(cur_at and z==cur_at["z"] and not isc)
    chips+=(f"<div class='p2-chip z{z}{' p2-chip-cur' if isc else ''}'>"
            f"<span class='p2c-n'>{'★' if isc else ('●' if same else '')}{esc(t['cn'])}</span>"
            f"<span class='p2c-d'>{esc(t['at_now']['own'][2:7])}</span>"
            f"<span class='p2c-z'>{zn(z)[:4]} {t['at_now']['v']:.0f}</span></div>")
n_same=sum(1 for t in TERMS if t["at_now"] and cur_at and t["at_now"]["z"]==cur_at["z"] and t["name"]!=AN["name"])
n_hard=sum(1 for t in TERMS if t["at_now"] and t["at_now"]["z"]=="H")
n_tot=sum(1 for t in TERMS if t["at_now"])

engine_rows=""
for k,v in A["engines"].items():
    cur=" class='eng-cur'" if k.startswith("整合") else ""
    engine_rows+=(f"<tr{cur}><td>{esc(k)}</td>"
                  f"<td class='mono'>{v['EASY']}%</td><td class='mono'>{v['UNCERTAIN']}%</td>"
                  f"<td class='mono'>{v['HARD']}%</td></tr>")

R8CSS="""
/* ---- R8 compact overrides ---- */
.r8-hero{padding:14px 22px 10px;max-width:1620px}
.r8-hero-row{display:flex;align-items:center;gap:10px;flex-wrap:wrap}
.r8-hero h1{font-size:22px;margin:0}
.r8-hero .hs{padding:4px 10px;font-size:11.5px}
.r8-hero-sub{color:var(--muted);font-size:11.5px;margin:6px 0 0;max-width:1200px;line-height:1.5}
.toc{padding:6px 16px}
.toc a{padding:3px 10px;font-size:12px}
.r8-eng{max-width:1620px;padding:8px 20px 0}
.eng-fold{background:var(--panel2);border:1px solid var(--line);border-radius:10px;padding:0}
.eng-fold>summary{cursor:pointer;padding:8px 14px;font-size:12.5px;color:var(--ink2);list-style:none;user-select:none}
.eng-fold>summary::-webkit-details-marker{display:none}
.eng-fold>summary::before{content:"▸ ";color:var(--muted)}
.eng-fold[open]>summary::before{content:"▾ "}
.eng-fold>summary:hover{color:var(--ink)}
.eng-fold>*:not(summary){margin-left:14px;margin-right:14px}
.eng-fold>p:last-child,.eng-fold>div:last-child{margin-bottom:12px}
.r6-grid{padding-top:10px;gap:12px}
.cy-block{padding:14px 16px 12px}
.cy-h2{font-size:17px}
.cy-sub{font-size:12px}
.theme-btn{top:8px;right:10px;padding:5px 12px;font-size:11.5px}
/* PANE 2 compact chip grid */
.r8-p2{max-width:1620px;padding:10px 20px 26px}
.r8-p2-head{display:flex;align-items:baseline;gap:12px;flex-wrap:wrap;margin-bottom:8px}
.r8-p2-head h2{font-size:16px;margin:0;border:0;padding:0}
.r8-p2-note{font-size:11.5px}
.p2-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(172px,1fr));gap:5px}
.p2-chip{display:flex;align-items:center;gap:6px;border:1px solid var(--line);border-radius:7px;
  padding:4px 9px;font-size:11px;background:var(--panel2)}
.p2-chip.zE{border-left:3px solid var(--easy-strip)}
.p2-chip.zU{border-left:3px solid var(--unc-strip)}
.p2-chip.zH{border-left:3px solid var(--hard-strip)}
.p2-chip-cur{outline:1.5px solid var(--chart-now,#7fd4ff)}
.p2c-n{font-weight:800;color:var(--head);white-space:nowrap;overflow:hidden;text-overflow:ellipsis;flex:1;min-width:0}
.p2c-d{color:var(--muted);font-variant-numeric:tabular-nums;flex:none}
.p2c-z{font-weight:800;flex:none;font-variant-numeric:tabular-nums}
.p2-chip.zE .p2c-z{color:var(--easy)}
.p2-chip.zU .p2c-z{color:var(--unc)}
.p2-chip.zH .p2c-z{color:var(--hard)}
.foot{padding:14px 22px 34px;font-size:11px}
"""

DATA_JSON=json.dumps({"anchor":A}, separators=(',',':'), ensure_ascii=False)

HTML=f"""<!doctype html>
<html lang="zh-Hant"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>美國總統 E/H MONEY R8 — 三引擎整合 A∩B∩C（{STAMP}）</title>
<style>{CSS}
{R8CSS}</style>
</head><body>
<button class="theme-btn" id="theme-btn" type="button">☀️ 淺色模式</button>
<header class="hero r8-hero">
  <div class="r8-hero-row">
    <h1>美國總統 E/H MONEY <span class="hero-r1">R8</span></h1>
    <span class="hs unc">現在 {esc(AN['now'])} · 週期第 {AN['cd_now']} 日 · {zn(cur_at['z'])} {cur_at['v']:.0f}</span>
    <span class="hs easy">整合 A∩B∩C：E {A['engines']['整合 A∩B∩C']['EASY']}% / U {A['engines']['整合 A∩B∩C']['UNCERTAIN']}% / H {A['engines']['整合 A∩B∩C']['HARD']}%</span>
    <span class="hs hard">距中期選舉 {DAYS_TO_MID} 日</span>
  </div>
  <p class="r8-hero-sub">基礎數據＝EasyHardMoney_NDX_2026R4.5.3_COMBINED_ABC「01_整合判區」的 EASY/UNCERTAIN/HARD（三票全同才判 E/H，其餘 U）。
  X 軸＝現任真實日曆（YEAR 0 當選 2024-11 → YEAR 5 卸任 2029-01-20，逐月標刻），歷任 25 屆按就任週期日對齊；
  R8 · 生成 {esc(HK.strftime('%Y-%m-%d %H:%M'))} 香港時間。</p>
</header>

<nav class="toc">
  <a href="#engines">整合規則</a><a href="#pane1">PANE 1</a><a href="#pane4">PANE 4</a><a href="#pane3">PANE 3</a><a href="#pane2">PANE 2</a>
</nav>

<section id="engines" class="block r8-eng">
<details class="eng-fold"><summary><b>整合規則與三引擎對照</b>（三票全同才判 EASY/HARD · 點開看門檻、佔比與跨層比較須知）</summary>
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
</details>
</section>

<div class="r6-grid">
<!-- ==================== PANE 1 ==================== -->
<section id="pane1" class="block r6-p1">
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
    </div>
    <div class="lay-bar">
      <button class="cy-btn" id="p1-lay-all" type="button">✕ 全部關閉</button>
      <span class="muted" style="font-size:11px">← 一鍵開合所有數據線；或逐條切換：</span>
      <span id="p1-layers" style="display:contents"></span>
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
    <h3 class="blk">轉區大事件（現屆 ＋ PANE 4 已開啟的前任，同步顯示）</h3>
    <div id="p1-tt"></div>
  </div>

</section>

<!-- ==================== PANE 4 ==================== -->
<aside id="pane4" class="block r6-p4">
  <div class="r6-cell">
    <div class="pane-tag p4">PANE 4</div>
    <h2 style="font-size:16px;margin:6px 0 2px">逐任總統比較</h2>
    <p class="muted" style="font-size:11.5px;margin:0 0 8px">
      按任一位＝在 PANE 1 疊上其軌跡，並把其<b>所有轉區大事件</b>同步列入 PANE 1 的表。</p>
    <div class="p4-head">
      <button class="cy-btn" id="p4-all" type="button">＋ 全部開啟</button>
      <span class="p4-count" id="p4-count">0 / 26</span>
    </div>
    <div class="p4-list" id="p4-list"></div>
    <div class="p4-note">「n轉」＝任內轉區次數；<i style="color:var(--easy);font-style:normal">·n離E</i>＝離開 EASY 的次數。
    圖上圓點＝轉區時點（顏色＝轉往的區），▼＝離開 EASY。</div>
  </div>
</aside>

<!-- ==================== PANE 3 ==================== -->
<section id="pane3" class="block r6-p3">
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

</div>

<!-- ==================== PANE 2 (bottom, compact) ==================== -->
<section id="pane2" class="block r8-p2">
  <div class="r8-p2-head">
    <div class="pane-tag p2">PANE 2</div>
    <h2>同位對照 · 週期第 {AN['cd_now']} 日</h2>
    <span class="muted r8-p2-note">現屆 <b class="t{cur_at['z']}">{zn(cur_at['z'])} {cur_at['v']:.0f}</b> ·
    {n_tot} 屆中 <b>{n_same} 屆</b>同區（●）· <b>{n_hard} 屆</b> HARD · 每格＝該屆走到同一週期位置時的自家日期與資金區</span>
  </div>
  <div class="p2-grid">{chips}</div>
</section>

<footer class="foot">
  <p>版本：R8（三引擎整合 A∩B∩C · 現任錨定 · 月份刻度 · 三 PANE）· 生成 {esc(HK.strftime('%Y-%m-%d %H:%M'))} 香港時間 · 檔名 {esc(FNAME)}</p>
  <p>資料來源：EasyHardMoney_NDX_2026R4.5.3_COMBINED_ABC（01_整合判區，A∩B∩C 三引擎共識，量測級 {nA} 屆每日判區）；
  美國總統任期百年 EasyHard 資金市場週期 R1（重建級 {nB} 屆逐屆窗口）。
  轉區原因：量測級取經核實的分段驅動＋事件庫，重建級取 R1 逐段依據注記；{ntr} 次轉區全部有注記。</p>
  <p class="disclaim">1937 年前就職日為 3 月 4 日，對齊以各自就職日為第 0 日，與日曆年帶有約 6 週漂移。
  現屆「未來」段（現在→卸任）留白，不作預測。本報告為市場史/框架研究，非投資建議。</p>
</footer>

<script>const DATA={DATA_JSON};{JS}</script>
</body></html>"""

for f in glob.glob(os.path.join(ROOT,"美國總統E-H MONEY R8 (*).html")): os.remove(f)
out=os.path.join(ROOT,FNAME)
open(out,"w").write(HTML)
print("written:",FNAME,f"({len(HTML)} bytes)")
