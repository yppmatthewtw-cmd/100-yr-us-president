import os
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# -*- coding: utf-8 -*-
"""Generate the presidency EASY/HARD money-cycle HTML report from computed + enriched data."""
import json, datetime, html

S = os.path.join(ROOT,"data")
CSS = open(os.path.join(ROOT,"assets","style.css")).read()
JS  = open(os.path.join(ROOT,"assets","cycle_engine.js")).read()
chart = json.load(open(f"{S}/chartdata.json"))
segments = json.load(open(f"{S}/segments.json"))
cycleyears = json.load(open(f"{S}/cycleyears.json"))
keydates = json.load(open(f"{S}/keydates.json"))
pkg = json.load(open(f"{S}/package.json"))
enriched = json.load(open(f"{S}/enriched.json"))
cycle    = json.load(open(f"{S}/cycle_aligned.json"))
ENR = {p['name']: p for p in enriched['presidents']}
SYN = enriched['synthesis']

PRES_META = {
 "Obama II": {"party":"D","full":"Barack Obama（第二任）","term":"2013–2017","cover":"數據自 2016-07 起（僅任期尾段）","cn":"奧巴馬 II"},
 "Trump I":  {"party":"R","full":"Donald Trump（第一任）","term":"2017–2021","cover":"全任期覆蓋","cn":"特朗普 I"},
 "Biden":    {"party":"D","full":"Joe Biden","term":"2021–2025","cover":"全任期覆蓋","cn":"拜登"},
 "Trump II": {"party":"R","full":"Donald Trump（第二任）","term":"2025–2029","cover":"進行中（數據至 2026-07-10）","cn":"特朗普 II"},
}
ORDER = ["Obama II","Trump I","Biden","Trump II"]

def esc(x): return html.escape(str(x)) if x is not None else ""

def zclass(z):
    return {"EASY":"easy","UNCERTAIN":"unc","HARD":"hard","E":"easy","U":"unc","H":"hard"}.get(z,"unc")
def zlabel(z):
    return {"EASY":"EASY 寬鬆","UNCERTAIN":"UNCERTAIN 震盪","HARD":"HARD 緊縮"}.get(z, z or "—")

# ---------- KPI helpers ----------
def pres_kpis(name):
    pts = chart[name]
    ret = (pts[-1]['n']/pts[0]['n']-1)*100
    from collections import Counter
    c = Counter(p['z'] for p in pts)
    n = len(pts)
    # worst drawdown across term
    peak=pts[0]['n']; mdd=0; pk=tr=None; runpk=pts[0]
    for p in pts:
        if p['n']>peak: peak=p['n']; runpk=p
        dd=(p['n']/peak-1)*100
        if dd<mdd: mdd=dd; pk=runpk; tr=p
    return {"ret":ret,"easy":c['E']/n*100,"unc":c['U']/n*100,"hard":c['H']/n*100,
            "mdd":mdd,"mdd_pk":pk['t'] if pk else None,"mdd_tr":tr['t'] if tr else None,
            "ndx0":pts[0]['n'],"ndx1":pts[-1]['n'],"t0":pts[0]['t'],"t1":pts[-1]['t']}

# ---------- section builders ----------
def build_kpi_row(name):
    k = pres_kpis(name)
    tiles = [
      ("NDX 期內表現", f"{k['ret']:+.1f}%", f"{k['ndx0']:.0f} → {k['ndx1']:.0f}", "ret"),
      ("EASY 佔比", f"{k['easy']:.0f}%", "寬鬆／順風日", "easy"),
      ("UNCERTAIN 佔比", f"{k['unc']:.0f}%", "震盪／未定日", "unc"),
      ("HARD 佔比", f"{k['hard']:.0f}%", "緊縮／熊市日", "hard"),
      ("期內最大回撤", f"{k['mdd']:.0f}%", (f"{k['mdd_pk']}→{k['mdd_tr']}" if k['mdd']<-2 else "—"), "dd"),
    ]
    cells=""
    for lab,val,sub,cl in tiles:
        cells += f'<div class="kpi kpi-{cl}"><div class="kpi-val">{esc(val)}</div><div class="kpi-lab">{esc(lab)}</div><div class="kpi-sub">{esc(sub)}</div></div>'
    return f'<div class="kpi-row">{cells}</div>'

def build_cycleyear_strip(name):
    yrs = cycleyears.get(name,{}).get('years',{})
    base = {1:"~+7%／蜜月＋開刀",2:"~+5% 最弱／-17% 回撤／中期見底",3:"~+16.8% 最強",4:"~+7% 前高後震"}
    cells=""
    for cy in ["1","2","3","4"]:
        y = yrs.get(cy)
        if not y:
            cells += f'<div class="cyc cyc-empty"><div class="cyc-h">第{cy}年</div><div class="cyc-empty-t">數據外／未到</div></div>'
            continue
        dom = "easy" if y['easy']>=max(y['unc'],y['hard']) else ("hard" if y['hard']>=y['unc'] else "unc")
        dd = f"最大回撤 {y['maxdd']:.0f}%" + (f"（{y['peak']}頂→{y['trough']}底）" if y['maxdd']<-3 else "")
        partial = "（部分）" if y['n']<200 else ""
        cells += (f'<div class="cyc cyc-{dom}"><div class="cyc-h">{esc(y["label"])} · {y["cal"]}{partial}</div>'
                  f'<div class="cyc-ret">{y["ret"]:+.1f}%</div>'
                  f'<div class="cyc-bars">'
                  f'<span class="seg easy" style="width:{y["easy"]*100:.0f}%" title="EASY {y["easy"]*100:.0f}%"></span>'
                  f'<span class="seg unc" style="width:{y["unc"]*100:.0f}%" title="UNCERTAIN {y["unc"]*100:.0f}%"></span>'
                  f'<span class="seg hard" style="width:{y["hard"]*100:.0f}%" title="HARD {y["hard"]*100:.0f}%"></span></div>'
                  f'<div class="cyc-sub">E {y["easy"]*100:.0f}% · U {y["unc"]*100:.0f}% · H {y["hard"]*100:.0f}%</div>'
                  f'<div class="cyc-dd">{esc(dd)}</div>'
                  f'<div class="cyc-arch">原型: {esc(base[int(cy)])}</div></div>')
    return f'<div class="cyc-strip">{cells}</div>'

def build_keydates(name):
    kd = keydates.get(name,[])
    rows=""
    for e in kd:
        z = e.get('zone')
        badge = f'<span class="zbadge {zclass(z)}">{zlabel(z)}</span>' if z else '<span class="zbadge out">數據外</span>'
        ndx = f"NDX {e['ndx']:.0f}" if e.get('ndx') else ""
        rows += f'<tr><td class="mono">{esc(e["date"])}</td><td>{esc(e["label"])}</td><td>{badge}</td><td class="mono">{esc(ndx)}</td></tr>'
    return f'<table class="kd"><thead><tr><th>日期</th><th>關鍵節點</th><th>當時資金區</th><th>NDX</th></tr></thead><tbody>{rows}</tbody></table>'

def build_events(name):
    ev = ENR.get(name,{}).get('events',[])
    if not ev: return '<p class="muted">（事件資料處理中）</p>'
    ev = sorted(ev, key=lambda e: e.get('date',''))
    catcls = {"Fed利率":"c-fed","貨幣政策/QE":"c-qe","戰爭/地緣":"c-war","財政/關稅":"c-fis","危機/黑天鵝":"c-crisis","市場":"c-mkt"}
    items=""
    for e in ev:
        cc = catcls.get(e.get('category'),"c-mkt")
        eff = f'<span class="ev-eff">{esc(e.get("ndx_effect"))}</span>' if e.get('ndx_effect') else ""
        items += (f'<div class="ev"><div class="ev-date mono">{esc(e.get("date"))}</div>'
                  f'<div class="ev-body"><span class="ev-cat {cc}">{esc(e.get("category"))}</span> '
                  f'<span class="ev-title">{esc(e.get("title"))}</span>{eff}'
                  f'<div class="ev-detail">{esc(e.get("detail"))}</div></div></div>')
    return f'<div class="ev-timeline">{items}</div>'

def build_rings(name):
    zd = ENR.get(name,{}).get('zone_drivers',[])
    if not zd: return '<p class="muted">（經濟環對應處理中）</p>'
    rows=""
    for d in zd:
        z = d.get('zone') or (d.get('segment','').split()[0] if d.get('segment') else '')
        rows += (f'<tr class="ring-{zclass(z)}">'
                 f'<td class="ring-seg"><span class="zbadge {zclass(z)}">{zlabel(z)}</span><div class="mono seg-lbl">{esc(d.get("segment"))}</div>'
                 f'<div class="ring-drv">{esc(d.get("driver"))}</div></td>'
                 f'<td>{esc(d.get("ring_political"))}</td>'
                 f'<td>{esc(d.get("ring_liquidity"))}</td>'
                 f'<td>{esc(d.get("ring_credit"))}</td>'
                 f'<td>{esc(d.get("ring_business"))}</td>'
                 f'<td>{esc(d.get("ring_blackswan"))}</td></tr>')
    return (f'<table class="rings"><thead><tr><th>實證分段 · 驅動力</th>'
            f'<th>① 政治環</th><th>② 流動性/Fed 環</th><th>③ 信用環</th><th>④ 景氣環</th><th>⑤ 黑天鵝/地緣環</th>'
            f'</tr></thead><tbody>{rows}</tbody></table>')

def build_narrative(name):
    e = ENR.get(name,{})
    nar = e.get('cycle_narrative','')
    conf = e.get('archetype_conformance','')
    return (f'<div class="narr"><div class="narr-block"><h4>資金週期全景（由當選到下台）</h4><p>{esc(nar)}</p></div>'
            f'<div class="narr-block conform"><h4>與百年總統週期原型的符合度</h4><p>{esc(conf)}</p></div></div>')

def build_president(name):
    m = PRES_META[name]
    party = "共和黨" if m['party']=="R" else "民主黨"
    return f'''
<section class="pres pres-{m['party']}" id="pres-{name.replace(' ','')}">
  <div class="pres-head">
    <div class="pres-tag {m['party']}">{esc(party)}</div>
    <div class="pres-title"><h2>{esc(m['full'])} <span class="pres-cn">{esc(m['cn'])}</span></h2>
      <div class="pres-meta">{esc(m['term'])} · {esc(m['cover'])}</div></div>
  </div>
  {build_kpi_row(name)}
  <h3 class="blk">總統週期年度分解（實證 vs 百年原型）</h3>
  {build_cycleyear_strip(name)}
  <h3 class="blk">關鍵節點定位</h3>
  {build_keydates(name)}
  <h3 class="blk">重大事件時間軸（Fed 利率 · 貨幣政策/QE · 戰爭/地緣 · 財政/關稅 · 危機）</h3>
  {build_events(name)}
  <h3 class="blk">各實證分段 × 經濟五環對應</h3>
  {build_rings(name)}
  {build_narrative(name)}
</section>'''


# ---------- unified presidency-cycle comparison ----------
CYCOL = {"Obama II":"#3987e5","Trump I":"#d95926","Biden":"#9085e9","Trump II":"#d55181"}

def build_cycle_charts():
    ms = "".join(
        f'<tr><td class="mono">{m["day"]:+d}</td><td>{esc(m["label"])}</td><td class="muted-td">{esc(m["note"])}</td></tr>'
        for m in cycle["milestones"])
    return f'''
<section id="cycle" class="block">
  <div class="cy-block">
    <div class="cy-head">
      <div>
        <h2 class="cy-h2">★ 統一總統週期比較：所有總統放在同一條就任週期軸上</h2>
        <p class="cy-sub">X 軸＝<b>總統週期日</b>（就職日 = 第 0 日，當選日約 −76 日，卸任 = 第 1461 日），
        Y 軸＝<b>Easy / Hard 指數</b>（18 指標加權合成分 0–100；≥70 EASY／40–70 UNCERTAIN／≤40 HARD）。
        每位總統一條獨立線，因此可直接看出「同一個週期位置上，各任總統的資金鬆緊有多不同」。</p>
        <p class="cy-axis-note">＊ 點擊下方圖例可開關任一總統；線末＊表示該任期數據不完整（每日數據自 2016-07 起）。</p>
      </div>
      <div class="cy-controls">
        <button class="cy-btn" id="cy-smooth" type="button">顯示：21日平滑</button>
      </div>
    </div>
    <div class="cy-legend" id="cy-legend"></div>
    <div class="cy-chart" id="cy-index"></div>
    <div class="cy-foot">讀法：線落入紅帶（≤40）＝該總統在該週期位置處於 HARD 資金環境。
    注意 <b>中期選舉 → 第2年終</b> 一段，特朗普 I 與拜登兩條線同時墜入紅帶——這正是百年規律「第2年最弱」的每日數據證據。</div>
  </div>

  <div class="cy-block">
    <div class="cy-head">
      <div>
        <h2 class="cy-h2">同一週期軸上的市場表現：NDX（就職日 = 100）</h2>
        <p class="cy-sub">同樣的 X 軸與同樣的顏色，改看指數本身。把上圖的「資金環境」與此圖的「市場結果」對讀，
        可看出資金區轉換與行情轉折的先後關係。</p>
      </div>
    </div>
    <div class="cy-chart" id="cy-ndx"></div>
    <div class="cy-foot">＊ 各任以自己的就職日收盤價為 100 重新指數化，故可跨任期直接比較漲跌幅。</div>
  </div>

  <h3 class="blk">週期關鍵節點定義（共用 X 軸刻度）</h3>
  <table class="kd"><thead><tr><th>週期日</th><th>關鍵節點</th><th>意義</th></tr></thead><tbody>{ms}</tbody></table>
</section>'''

def build_phase_matrix():
    phases = cycle["phases"]; mat = cycle["matrix"]; arch = cycle["archetype"]
    def cls(v):
        if v is None: return "pm-na"
        return "pm-E" if v>=70 else ("pm-H" if v<=40 else "pm-U")
    head = '<tr><th class="pm-ph">週期階段</th>'
    for n in ORDER:
        if n not in mat: continue
        head += (f'<th><span class="pm-pres"><i style="background:{CYCOL[n]}"></i>'
                 f'{esc(PRES_META[n]["cn"])}</span></th>')
    head += '<th>四任平均</th></tr>'
    rows=""
    for ph in phases:
        k=ph["key"]
        rows += f'<tr><td class="pm-ph">{esc(k)}<small>{esc(ph["desc"])}</small></td>'
        for n in ORDER:
            if n not in mat: continue
            v = mat[n].get(k)
            if not v:
                rows += '<td class="pm-na">數據外</td>'
            else:
                rows += (f'<td class="{cls(v["avg"])}"><div class="pm-v">{v["avg"]:.1f}</div>'
                         f'<div class="pm-s">E{v["easy"]}/U{v["unc"]}/H{v["hard"]}％ · NDX {v["ndx"]:+.1f}%</div></td>')
        a = arch.get(k,{})
        av = a.get("avg")
        rows += (f'<td class="pm-avg"><div class="pm-v">{av:.1f}</div>'
                 f'<div class="pm-s">{a.get("n_pres",0)} 任平均</div></td>' if av is not None
                 else '<td class="pm-na">—</td>')
        rows += '</tr>'
    return f'''
<section id="phases" class="block">
  <h2>週期階段矩陣：同一階段、不同總統的 Easy/Hard 指數</h2>
  <p class="muted">把連續的週期軸切成 8 個階段，每格＝該總統在該階段的平均 Easy/Hard 指數（顏色＝所屬區），
  下方小字為該階段的三區日數佔比與 NDX 階段漲跌。最後一欄為跨總統平均＝<b>本框架的「週期原型」實證值</b>。</p>
  <div class="pm-wrap"><table class="pm"><thead>{head}</thead><tbody>{rows}</tbody></table></div>
  <div class="callout" style="margin-top:16px">
    <h4>矩陣讀出的三條規律</h4>
    <p>① <b>「第2年下半」是全週期唯一的 HARD 階段</b>——跨任平均僅 {arch["第2年下 Y2 H2"]["avg"]}，
    特朗普 I（{mat["Trump I"]["第2年下 Y2 H2"]["avg"]}）與拜登（{mat["Biden"]["第2年下 Y2 H2"]["avg"]}）同時墜入紅區。
    ② <b>第3年回到 EASY</b>（跨任平均 {arch["第3年 Year 3"]["avg"]}），印證「第3年托市最強」。
    ③ <b>交接期與第1年是全週期最寬鬆的起點</b>（{arch["交接期 Transition"]["avg"]} / {arch["第1年 Year 1"]["avg"]}）＝蜜月期的量化證據。</p>
  </div>
</section>'''

# ---------- cross-president comparison ----------
def build_comparison():
    comp = SYN.get('comparison',[])
    rows=""
    for c in comp:
        rows += (f'<tr><td class="cmp-p">{esc(c.get("president"))}</td>'
                 f'<td>{esc(c.get("y1"))}</td><td>{esc(c.get("y2"))}</td>'
                 f'<td>{esc(c.get("y3"))}</td><td>{esc(c.get("y4"))}</td>'
                 f'<td class="cmp-cf">{esc(c.get("conforms"))}</td><td>{esc(c.get("note"))}</td></tr>')
    tbl = (f'<table class="cmp"><thead><tr><th>總統</th><th>第1年 就職</th><th>第2年 中期選舉</th>'
           f'<th>第3年 大選前</th><th>第4年 大選</th><th>符合度</th><th>點題</th></tr></thead><tbody>{rows}</tbody></table>') if comp else ""
    exc = SYN.get('exceptions',[])
    excards = "".join(f'<div class="exc"><div class="exc-n">{esc(x.get("name"))}</div><div class="exc-d">{esc(x.get("desc"))}</div></div>' for x in exc)
    excblock = f'<h3 class="blk">偏離百年原型的例外</h3><div class="exc-grid">{excards}</div>' if exc else ""
    summ = f'<div class="callout"><h4>橫向總結：四個實證週期如何印證/修正百年規律</h4><p>{esc(SYN.get("summary"))}</p></div>' if SYN.get("summary") else ""
    return f'{tbl}{excblock}{summ}'

# ---------- R1 100-year table ----------
def build_hist_table():
    rows=""
    covered = {"Obama II","Trump I","Biden","Trump II"}
    for h in pkg['hist']:
        name = h['pres']
        base = name.split()[0] + (" " + name.split()[1] if len(name.split())>1 and name.split()[1] in ("I","II","41","43") else "")
        is_cov = any(name.startswith(k) for k in covered)
        cls = ' class="cov"' if is_cov else ''
        badge = '<span class="cov-b">★本次實證</span>' if is_cov else ''
        rows += (f'<tr{cls}><td class="hist-p">{esc(name)} {badge}</td>'
                 f'<td class="easy-cell">{esc(h.get("easy"))}</td>'
                 f'<td class="hard-cell">{esc(h.get("hard"))}</td>'
                 f'<td class="ev-cell">{esc(h.get("events"))}</td></tr>')
    return (f'<table class="hist"><thead><tr><th>總統（任期）</th><th>EASY Money 窗口</th>'
            f'<th>HARD Money 窗口</th><th>關鍵數據與事件</th></tr></thead><tbody>{rows}</tbody></table>')

def build_cycstats():
    rows=""
    for c in pkg['cycstats']:
        rows += f'<tr><td>{esc(c["year"])}</td><td class="mono">{esc(c["ret"])}</td><td class="mono">{esc(c["upratio"])}</td><td>{esc(c["feat"])}</td></tr>'
    return (f'<table class="cs"><thead><tr><th>任期年份</th><th>平均回報</th><th>上升年比例</th><th>特徵</th></tr></thead><tbody>{rows}</tbody></table>')

def build_policy():
    rows=""
    codemap={1:("寬鬆","p-e"),0:("中性","p-u"),-1:("緊縮","p-h")}
    for p in pkg['l1policy']:
        lab,cl = codemap.get(p['code'],("—","p-u"))
        rows += f'<tr><td class="mono">{esc(p["date"])}</td><td><span class="pill {cl}">{lab}</span></td><td>{esc(p["state"])}</td></tr>'
    return f'<table class="pol"><thead><tr><th>生效日</th><th>方向</th><th>Fed 政策狀態</th></tr></thead><tbody>{rows}</tbody></table>'

# ---------- assemble ----------
GEN_DATE = "2026-07-25"
CHART_JSON = json.dumps({"cycle":cycle}, separators=(',',':'), ensure_ascii=False)

pres_sections = "\n".join(build_president(n) for n in ORDER)

HTML = f'''<!doctype html>
<html lang="zh-Hant"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>美國總統任期 × Easy / Hard 資金市場週期 R1</title>
<style>{CSS}</style>
</head><body>
<header class="hero">
  <div class="hero-eyebrow">A-(Fable) EasyHardMoney 三區指標庫 · NDX 十年每日分段 · 2026 R4.5.3</div>
  <h1>美國總統任期 × Easy / Hard 資金市場週期 <span class="hero-r1">R1</span></h1>
  <div class="hero-sub">以 <b>NDX（納指100）2016-07 → 2026-07 共 2,515 個交易日</b>的三區（EASY／UNCERTAIN／HARD）實證數據，
  重新定義各任總統「由當選到下台」的資金鬆緊週期，<b>並把所有總統疊在同一條就任週期軸上直接比較</b>，再對照百年總統週期原型與五個經濟環。</div>
  <div class="hero-strip">
    <span class="hs easy">EASY 1,757 日 · 69.9%</span>
    <span class="hs unc">UNCERTAIN 441 日 · 17.5%</span>
    <span class="hs hard">HARD 317 日 · 12.6%</span>
  </div>
  <div class="hero-note">判區引擎：18 項量化指標（技術/趨勢、廣度、流動性/政策、信用、波動率、情緒）加權合成分 ≥70=EASY／40–70=UNCERTAIN／≤40=HARD。生成日 {GEN_DATE}。</div>
</header>

<nav class="toc">
  <a href="#method">方法</a><a href="#cycle">★週期比較圖</a><a href="#phases">階段矩陣</a><a href="#law">百年規律</a><a href="#compare">橫向比較</a>
  <a href="#pres-ObamaII">奧巴馬II</a><a href="#pres-TrumpI">特朗普I</a><a href="#pres-Biden">拜登</a><a href="#pres-TrumpII">特朗普II</a>
  <a href="#hist">百年全表</a><a href="#policy">Fed 步階</a>
</nav>

<section id="method" class="block">
  <h2>方法與框架</h2>
  <div class="two-col">
    <div class="panel">
      <h4>三區資金市場（Easy / Hard Money）</h4>
      <p><b class="tE">EASY 寬鬆</b>：流動性/趨勢順風、順勢做多勝率高的時段。<br>
      <b class="tU">UNCERTAIN 震盪</b>：方向未定、洗倉，賺錢需擇時。<br>
      <b class="tH">HARD 緊縮</b>：緊縮/熊市/高波動、賺錢困難時段。</p>
      <p class="muted">本報告的創新：不再只用定性描述，而是用 NDX 每日 18 指標合成分「逐日判區」，再平滑成制度級分段（最短 10 交易日），
      使每任總統的 Easy/Hard 段有精確起訖日與 NDX 點位。</p>
    </div>
    <div class="panel">
      <h4>五個經濟環（逐段對應）</h4>
      <ol class="rings-legend">
        <li><b>① 政治/總統週期</b>：第1年開刀、第2年中期選舉最弱、第3年托市最強、第4年前高後震。</li>
        <li><b>② 流動性/Fed 環</b>：加息/減息/QE/QT/淨流動性。</li>
        <li><b>③ 信用環</b>：HY 高收益債利差（股市測謊機）。</li>
        <li><b>④ 實體經濟/景氣環</b>：衰退/擴張、就業、盈利。</li>
        <li><b>⑤ 黑天鵝/地緣環</b>：戰爭、疫情、關稅等外生衝擊。</li>
      </ol>
    </div>
  </div>
</section>

<section id="law" class="block">
  <h2>百年總統週期規律（統計底稿）</h2>
  <p class="muted">S&amp;P 500 總統週期統計（1950 年後為主樣本）——Easy/Hard 的量化底稿。下方各任實證數據將逐一與此原型對錶。</p>
  {build_cycstats()}
  <div class="lawcards">
    <div class="lawcard"><b>第2年＝宿命 HARD 位</b><span>百年 26 屆中 15 次大級別底部落在第2年（中期選舉年）；平均年內 -17% 回撤為四年之最。</span></div>
    <div class="lawcard"><b>第3年＝宿命 EASY 位</b><span>四年最強（~+16.8%）；1950 後 19 屆僅 1 次輕微下跌。政治托市極大化。</span></div>
    <div class="lawcard"><b>黃金 3 季</b><span>第2年Q4 → 第3年Q2，平均 ~+20%、勝率 ~90%＝16 季中最肥一段。</span></div>
    <div class="lawcard"><b>四類例外</b><span>債務通縮 / 失控通脹 / 信用危機 / 外生黑天鵝——流動性或黑天鵝壓倒政治週期之時。</span></div>
  </div>
</section>

{build_cycle_charts()}

{build_phase_matrix()}

<section id="compare" class="block">
  <h2>橫向總統週期比較（2016–2026 四任實證）</h2>
  {build_comparison()}
</section>

<div class="block">
  <h2 class="section-lead">逐任總統：由當選到下台的資金週期</h2>
  {pres_sections}
</div>

<section id="hist" class="block">
  <h2>百年逐屆 Easy / Hard（1925–2026，R1 全表）</h2>
  <p class="muted">★ 標記者為本報告以 NDX 每日數據實證重定義的任期（2016 年後）；其餘保留 R1 百年定性框架。</p>
  {build_hist_table()}
</section>

<section id="policy" class="block">
  <h2>Fed L1 政策方向步階（公開紀錄重建）</h2>
  <p class="muted">Fed 政策本質是步階函數，只在 FOMC 決議/明確指引轉向時改變——這是流動性環的骨架。</p>
  {build_policy()}
</section>

<footer class="foot">
  <p>資料來源：A-(Fable) EasyHardMoney 三區指標庫及 NDX 十年每日分段 2026R4.5.3_2（每日判區、18 指標合成分、Fed 步階）；美國總統任期百年 EasyHard 資金市場週期 R1（百年定性框架與統計）。</p>
  <p>方法：以 02A 每日 ZONE 欄為實證輸入，平滑成最短 10 交易日的制度級分段；總統週期年度統計以就職年為第1年、日曆年切分；重大事件與經濟環對應經多代理查核。</p>
  <p class="disclaim">本報告為市場史/框架研究，非投資建議。平均值因統計口徑略有出入，形態結論穩健。</p>
</footer>

<script>const DATA={CHART_JSON};{JS}</script>
</body></html>'''

open(os.path.join(ROOT,"美國總統任期_EasyHard資金市場週期_R1.html"),"w").write(HTML)
# also write to a stable scratch path

print("HTML written:", len(HTML), "bytes")
