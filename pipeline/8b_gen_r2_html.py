# -*- coding: utf-8 -*-
"""R2 — build the 100-year (26-term) presidency money-cycle comparison report."""
import os, json, html
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
S=os.path.join(ROOT,"data")
CSS=open(os.path.join(ROOT,"assets","style.css")).read()
JS =open(os.path.join(ROOT,"assets","century_engine.js")).read()
C  =json.load(open(f"{S}/century.json"))
pkg=json.load(open(f"{S}/package.json"))

def esc(x): return html.escape(str(x)) if x is not None else ""
M,ORDER,MAT,PS,YS = C["meta"],C["order"],C["matrix"],C["phase_summary"],C["yearstats"]
TR,MT = C["troughs"],C["midterm"]

def zc(v):
    if v is None: return "pm-na"
    return "pm-E" if v>=70 else ("pm-H" if v<=40 else "pm-U")

# ---------- phase matrix: 26 rows x 8 phases ----------
def phase_matrix():
    ph=C["phases"]
    head="<tr><th class='pm-ph'>總統（任期）</th><th>層</th>"+ "".join(
        f"<th>{esc(p['key'].split()[0])}<br><small>{esc(p['desc'])}</small></th>" for p in ph)+"</tr>"
    rows=""
    for n in ORDER:
        m=M[n]
        tier_cls={"A":"tier-A","B":"tier-B","混合":"tier-M"}[m["tier"]]
        rows+=(f"<tr><td class='pm-ph'>{esc(m['cn'])}<small>{esc(m['inaug'][:4])}–{esc(m['end'][:4])} · {esc(m['era'])}</small></td>"
               f"<td class='pm-tier {tier_cls}'>{esc(m['tier'])}</td>")
        for p in ph:
            v=MAT[n].get(p["key"])
            if not v: rows+="<td class='pm-na'>—</td>"
            else:
                rows+=(f"<td class='{zc(v['avg'])}'><div class='pm-v'>{v['avg']:.0f}</div>"
                       f"<div class='pm-s'>H{v['hard']}%</div></td>")
        rows+="</tr>"
    # summary row
    rows+="<tr class='pm-sum'><td class='pm-ph'>26 屆彙總<small>平均 / 中位</small></td><td class='pm-tier'>—</td>"
    for p in ph:
        s=PS[p["key"]]
        rows+=(f"<td class='{zc(s['avg'])}'><div class='pm-v'>{s['avg']:.0f}</div>"
               f"<div class='pm-s'>中位 {s['med']:.0f} · {s['terms_hard']}/{s['terms']} 屆HARD</div></td>")
    rows+="</tr>"
    return f"<div class='pm-wrap'><table class='pm pm-century'><thead>{head}</thead><tbody>{rows}</tbody></table></div>"

# ---------- trough distribution ----------
def trough_block():
    yd=C["trough_year_dist"]; tot=sum(yd.values())
    bars=""
    for k in ["第1年","第2年","第3年","第4年"]:
        v=yd.get(k,0); p=v/tot*100 if tot else 0
        hot=" hot" if k=="第2年" else ""
        bars+=(f"<div class='tb-row{hot}'><div class='tb-lab'>{esc(k)}</div>"
               f"<div class='tb-track'><div class='tb-fill{hot}' style='width:{p:.1f}%'></div></div>"
               f"<div class='tb-val'>{v} 屆 · {p:.0f}%</div></div>")
    md=C["trough_month_dist"]; mx=max(md.values()) or 1
    mbars=""
    for m in range(1,13):
        v=md.get(str(m), md.get(m,0))
        h=v/mx*100
        hot=" hot" if m in (10,12) else ""
        mbars+=(f"<div class='mb-col'><div class='mb-bar-wrap'><div class='mb-bar{hot}' style='height:{h:.0f}%'></div></div>"
                f"<div class='mb-n'>{v or ''}</div><div class='mb-m'>{m}</div></div>")
    mt_rows="".join(
        f"<tr><td>{esc(M[x['term']]['cn']) if x['term'] in M else esc(x['term'])}</td>"
        f"<td class='mono'>{esc(x['date'])}</td><td class='mono'>{x['year']}</td></tr>"
        for x in MT["list"])
    return f"""
<section id="trough" class="block">
  <h2>見底位置：R1「大底落在第2年」的百年驗證</h2>
  <p class="muted">此處不使用指數平均值（階梯式重建會讓 HARD 區段的最低值落在區段起點，是方法假象），
  而是逐屆採用<b>有紀錄的實際收市見底日</b>，再換算成週期日。</p>
  <div class="two-col">
    <div class="panel">
      <h4>各任「任內最大底部」落在哪一個週期年（26 屆）</h4>
      <div class="tb">{bars}</div>
      <p class="muted" style="margin-top:12px">
        <b>15/26 屆（58%）的任內大底落在第2年（中期選舉年）</b>——與 R1 表列的 15 次樣本完全一致，
        且第3年僅 1 屆（4%），是全週期最不容易見底的一年。</p>
    </div>
    <div class="panel">
      <h4>見底月份分佈（26 屆）</h4>
      <div class="mb">{mbars}</div>
      <p class="muted" style="margin-top:10px">
        R1 的 15 次中期年大底中：8–10 月 {MT['aug_oct']}/15、
        <b>Q4（10–12月）{MT['q4']}/15</b>、其中 12 月 {MT['dec']}/15。
        修正：R1 原述「集中 8–10 月」方向正確，但更準確的說法是<b>集中於 Q4</b>；
        1974、1994、2018、2022 四次都落在 12 月，皆因 Fed 拖到年底才轉向。</p>
    </div>
  </div>
  <h3 class="blk">R1 明列的 15 次中期選舉年大底</h3>
  <div class="pm-wrap"><table class="kd mt-list"><thead><tr><th>總統（任期）</th><th>見底日</th><th>年份</th></tr></thead>
  <tbody>{mt_rows}</tbody></table></div>
</section>"""

# ---------- cycle-year stats across 26 terms ----------
def yearstats_block():
    rows=""
    arche={"第1年 就職年":"~+7% 蜜月＋開刀","第2年 中期選舉年":"~+5% 最弱／-17% 回撤",
           "第3年 大選前年":"~+16.8% 最強","第4年 大選年":"~+7% 前高後震"}
    for k,y in YS.items():
        rows+=(f"<tr><td class='ys-y'>{esc(k)}</td>"
               f"<td class='{zc(y['avg'])} ys-v'>{y['avg']:.1f}</td>"
               f"<td class='mono'>{y['med']:.1f}</td>"
               f"<td class='mono'>{y['hard_terms']}/{y['terms']}</td>"
               f"<td class='mono'>{y['easy_terms']}/{y['terms']}</td>"
               f"<td>{esc(M[y['worst']]['cn'])} <span class='mono'>({y['worst_v']:.0f})</span></td>"
               f"<td>{esc(M[y['best']]['cn'])} <span class='mono'>({y['best_v']:.0f})</span></td>"
               f"<td class='muted-td'>{esc(arche.get(k,''))}</td></tr>")
    return (f"<table class='cs'><thead><tr><th>週期年</th><th>平均指數</th><th>中位</th>"
            f"<th>HARD 屆數</th><th>EASY 屆數</th><th>最差一屆</th><th>最佳一屆</th><th>R1 原型</th>"
            f"</tr></thead><tbody>{rows}</tbody></table>")

# ---------- per-term Tier B segment detail ----------
def segments_block():
    rows=""
    for n in ORDER:
        m=M[n]
        if not m["segs"]:
            rows+=(f"<tr class='seg-a'><td class='seg-p'>{esc(m['cn'])}<small>{esc(m['inaug'][:4])}–{esc(m['end'][:4])}</small></td>"
                   f"<td colspan='4' class='muted-td'>Tier A 量測級——直接採用每日 18 指標加權合成分，"
                   f"不使用重建分段（見 R1 報告的逐日分段）。</td></tr>")
            continue
        for i,s in enumerate(m["segs"]):
            zz="E" if s["v"]>=70 else ("H" if s["v"]<=40 else "U")
            rows+=("<tr>"+(f"<td class='seg-p' rowspan='{len(m['segs'])}'>{esc(m['cn'])}"
                           f"<small>{esc(m['inaug'][:4])}–{esc(m['end'][:4])} · {esc(m['era'])}</small></td>" if i==0 else "")
                   +f"<td class='mono'>{esc(s['s'])} → {esc(s['e'])}</td>"
                   +f"<td class='{zc(s['v'])} seg-v'>{s['v']}</td>"
                   +f"<td><span class='lv-tag'>{esc(s['lv'])}</span></td>"
                   +f"<td class='muted-td'>{esc(s['note'])}</td></tr>")
    return (f"<div class='pm-wrap'><table class='segs'><thead><tr><th>總統（任期）</th><th>期間</th>"
            f"<th>指數</th><th>級別</th><th>依據／事件</th></tr></thead><tbody>{rows}</tbody></table></div>")

RUB="".join(f"<div class='rub'><span class='rub-v'>{v}</span><span class='rub-k'>{esc(k)}</span></div>"
            for k,v in sorted(C["rubric"].items(), key=lambda kv:-kv[1]))

DATA_JSON=json.dumps({"century":C}, separators=(',',':'), ensure_ascii=False)
nA=sum(1 for n in ORDER if M[n]["tier"]=="A")
nB=sum(1 for n in ORDER if M[n]["tier"]=="B")

HTML=f"""<!doctype html>
<html lang="zh-Hant"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>美國總統任期 × Easy / Hard 資金市場週期 R2（百年 26 屆）</title>
<style>{CSS}</style>
</head><body>
<header class="hero">
  <div class="hero-eyebrow">百年 26 屆 · 1925–2029 · 統一總統週期軸</div>
  <h1>美國總統任期 × Easy / Hard 資金市場週期 <span class="hero-r1">R2</span></h1>
  <div class="hero-sub">把 <b>1925–2029 全部 26 屆</b>美國總統任期，全部疊在<b>同一條就任週期軸</b>上：
  X 軸＝總統週期日（當選 → 就職 → 首100日 → 第1/2/3/4 年 → 中期選舉 → 大選 → 卸任），
  Y 軸＝ Easy / Hard 指數。每屆一條獨立線，加上 26 屆中位數與四分位帶，直接看出百年週期的共同形狀。</div>
  <div class="hero-strip">
    <span class="hs easy">26 屆全覆蓋 1925–2029</span>
    <span class="hs unc">{nA} 屆量測級 · {nB} 屆重建級</span>
    <span class="hs hard">15/26 屆大底落在第2年</span>
  </div>
  <div class="hero-note">R1＝以 NDX 每日 18 指標實證重定義的 4 屆高解析版；R2＝在同一框架下把覆蓋範圍擴至百年 26 屆。</div>
</header>

<nav class="toc">
  <a href="#tiers">雙層數據</a><a href="#main">★百年主圖</a><a href="#small">26屆小倍數</a>
  <a href="#matrix">階段矩陣</a><a href="#trough">見底位置</a><a href="#years">週期年統計</a><a href="#segs">逐屆分段</a>
</nav>

<section id="tiers" class="block">
  <h2>先講數據誠實性：兩層資料，不混為一談</h2>
  <div class="two-col">
    <div class="panel tier-panel tier-A-panel">
      <h4><span class="tier-badge tier-A">TIER A</span> 量測級（{nA} 屆）</h4>
      <p>2016-07 → 2026-07。直接採用 A-(Fable) 檔案的<b>每日 18 指標加權合成分</b>
      （技術/趨勢、廣度、流動性/政策、信用、波動率、情緒），逐日判區，日級解析度。</p>
      <p class="muted">涵蓋：特朗普 I、拜登、特朗普 II（奧巴馬 II 為混合，2016-07 起為量測級）。</p>
    </div>
    <div class="panel tier-panel tier-B-panel">
      <h4><span class="tier-badge tier-B">TIER B</span> 重建級（{nB} 屆）</h4>
      <p>1925 → 2016-07。<b>沒有每日指標數據</b>，故依 R1 自身列明的逐屆 EASY / HARD 窗口，
      對照有紀錄的市場史（見頂見底日、Fed 轉向、危機）轉寫為<b>分段式階梯指數</b>。</p>
      <p class="muted"><b>這是分段級、不是偽造的每日序列</b>——圖上呈現為階梯線，級別對照下方公開評分表。</p>
    </div>
  </div>
  <h3 class="blk">Tier B 評分表（公開、可稽核、可重算）</h3>
  <div class="rubric">{RUB}</div>
  <p class="muted">每一段的級別與依據，全部逐條列於下方「逐屆分段全表」，可直接與 R1 原文對照。</p>
</section>

<section id="main" class="block">
  <div class="cy-block">
    <div class="cy-head">
      <div>
        <h2 class="cy-h2">★ 百年資金區熱圖：26 屆總統 × 同一條就任週期軸</h2>
        <p class="cy-sub">每一橫列＝一屆總統任期（由上而下依年代排序），橫軸＝總統週期日。
        顏色＝該屆在該週期位置所處的資金區：<b class="tE">綠 EASY</b>／<b class="tU">黃 UNCERTAIN</b>／<b class="tH">紅 HARD</b>。
        列左小色條標示資料層（綠＝量測級 A、灰＝重建級 B、黃＝混合）；
        列上三角＝該屆<b>有紀錄的實際見底日</b>（<span style="color:#ffd479">黃色</span>＝落在第2年中期選舉年，即 R1 的 15 次樣本）。
        點擊左側名稱可聚焦該屆。</p>
      </div>
      <div class="cy-controls" id="ct-modes">
        <button class="cy-btn" data-mode="era" type="button">依年代</button>
        <button class="cy-btn" data-mode="party" type="button">依政黨</button>
        <button class="cy-btn" data-mode="tier" type="button">依資料層</button>
        <button class="cy-btn" data-mode="none" type="button">不分色</button>
      </div>
    </div>
    <div class="cy-chart" id="ct-heat"></div>
    <div class="cy-foot">底部紅色面積＝<b>同一週期位置上，26 屆之中有多少比例處於 HARD</b>。
    它的兩個高峰分別落在<b>第1年後段～第2年上半</b>與<b>第4年前段</b>，而<b>第3年是全週期最低的一段</b>——
    這就是百年總統週期在資金面上的骨架。</div>
  </div>

  <div class="cy-block">
    <div class="cy-head">
      <div>
        <h2 class="cy-h2">週期原型曲線：26 屆中位數與四分位帶</h2>
        <p class="cy-sub"><b class="med-k">粗黃線＝26 屆中位數</b>，灰帶＝四分位區間（P25–P75，中間一半的任期落在此範圍），
        背景細線＝26 屆各自的軌跡。中位數與四分位帶已作 13 週平滑，
        因為 22 屆重建級為階梯序列，未平滑的中位數會隨階梯跳動而失去形狀。</p>
      </div>
    </div>
    <div class="ct-legend" id="ct-legend"></div>
    <div class="cy-chart" id="ct-main"></div>
    <div class="cy-foot">中位數線的形狀就是「百年總統週期的平均資金環境」：
    就職後一路偏 EASY，<b>第1年後段至第2年上半明顯下沉</b>，中期選舉後回升，<b>第3年重回全週期最高</b>，第4年高位震盪。</div>
  </div>
</section>

<section id="small" class="block">
  <h2>26 屆逐屆小倍數（同一週期軸、同一 Y 尺度）</h2>
  <p class="muted">每格＝一屆，X 軸同為週期日（灰線＝第1/2/3年分界，白線＝就職日），
  底部紅色三角＝該屆<b>有紀錄的實際見底日</b>。點擊卡片可在上方主圖中highlight該屆。</p>
  <div class="sm-grid" id="ct-small"></div>
</section>

<section id="matrix" class="block">
  <h2>週期階段矩陣：26 屆 × 8 個週期階段</h2>
  <p class="muted">每格＝該屆在該階段的平均 Easy/Hard 指數（顏色＝所屬區），小字為該階段判 HARD 的時間佔比。
  最底列為 26 屆彙總。「層」欄標示該屆屬量測級(A)／重建級(B)／混合。</p>
  {phase_matrix()}
</section>

{trough_block()}

<section id="years" class="block">
  <h2>總統週期年統計（26 屆）</h2>
  <p class="muted">以 Easy/Hard 指數平均值衡量四個週期年的資金環境，並與 R1 的百年報酬原型對照。</p>
  {yearstats_block()}
  <div class="callout">
    <h4>百年 26 屆的三條結論</h4>
    <p>① <b>第3年確實是全週期最寬鬆的一年</b>——平均 {YS['第3年 大選前年']['avg']:.1f}、中位 {YS['第3年 大選前年']['med']:.1f}，
    26 屆中僅 {YS['第3年 大選前年']['hard_terms']} 屆落入 HARD，且僅 1 屆的任內大底出現在此年。R1 的「第3年最強」在百年尺度成立。
    ② <b>「第2年最弱」要分開兩種講法</b>：以<b>見底位置</b>論完全成立（15/26 屆大底落在第2年）；
    但以<b>全年平均資金環境</b>論，第1年（{YS['第1年 就職年']['avg']:.1f}）與第2年（{YS['第2年 中期選舉年']['avg']:.1f}）相近——
    因為第2年常是「先重挫、後暴力反彈」，把全年平均拉回。這正是 R1 說的「前弱後強」。
    ③ <b>見底月份應更新為 Q4 而非 8–10 月</b>：15 次中期年大底裡 Q4 佔 {MT['q4']}/15，
    其中 12 月 {MT['dec']}/15（1974、1994、2018、2022）——現代由 Fed 轉向時點決定，普遍比舊樣本更晚。</p>
  </div>
</section>

<section id="segs" class="block">
  <h2>逐屆 Easy / Hard 分段全表（Tier B 明細）</h2>
  <p class="muted">重建級任期的每一段：期間、指數、級別與依據事件。可逐條與 R1 原表的 EASY／HARD 窗口對照稽核。</p>
  {segments_block()}
</section>

<section class="block">
  <h2>百年逐屆 Easy / Hard（R1 原表）</h2>
  <p class="muted">下表為來源 R1 的原始定性框架，本報告的 Tier B 分段即以此為主要依據。</p>
  <table class="hist"><thead><tr><th>總統（任期）</th><th>EASY Money 窗口</th><th>HARD Money 窗口</th><th>關鍵數據與事件</th></tr></thead>
  <tbody>{''.join(f"<tr><td class='hist-p'>{esc(h['pres'])}</td><td class='easy-cell'>{esc(h.get('easy'))}</td><td class='hard-cell'>{esc(h.get('hard'))}</td><td class='ev-cell'>{esc(h.get('events'))}</td></tr>" for h in pkg['hist'])}</tbody></table>
</section>

<footer class="foot">
  <p>資料來源：A-(Fable) EasyHardMoney 三區指標庫及 NDX 十年每日分段 2026R4.5.3_2（Tier A 每日判區、18 指標合成分、Fed 步階）；
  美國總統任期百年 EasyHard 資金市場週期 R1（Tier B 逐屆 EASY/HARD 窗口與百年統計）。</p>
  <p>方法：Tier A 直接取每日合成分；Tier B 依 R1 窗口＋有紀錄市場史轉寫為分段階梯指數（評分表見上）。
  週期對齊以就職日為第 0 日，週抽樣；交接期（週期日 &lt; 0）取前一任的區段值。見底位置採實際見底日，非由指數推導。</p>
  <p class="disclaim">本報告為市場史/框架研究，非投資建議。Tier B 為依據公開紀錄的重建，非量測數據，判讀時請留意層級標示。</p>
</footer>

<script>const DATA={DATA_JSON};{JS}</script>
</body></html>"""

out=os.path.join(ROOT,"美國總統任期_EasyHard資金市場週期_R2.html")
open(out,"w").write(HTML)
print("R2 HTML written:",len(HTML),"bytes →",os.path.basename(out))
