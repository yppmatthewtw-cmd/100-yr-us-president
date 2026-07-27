# -*- coding: utf-8 -*-
"""Win-rate analysis: which structural periods of the presidency cycle have the
highest win rate (probability of a positive/EASY outcome)?

Two independent sources, kept separate and cross-checked:

  SOURCE A (authoritative, cited)  — R1's own S&P 500 1950-2024 statistics
      ("上升年比例" = the literal win-rate column in the source spreadsheet).
  SOURCE B (this project's own empirical reconstruction) —
      B1: phase-level P(EASY zone) aggregated across all 26 terms
          (century.json matrix, weighted by trading-day count) — a systemic,
          engine-based proxy for "win rate" spanning the full 100 years.
      B2: real-NDX month-win-rate (% of calendar months with a positive
          close-to-close return) computed ONLY over the measured window
          (2016-07 to 2026-07, daily.json) sliced by cycle-year and by phase —
          genuine price-based evidence, not reconstructed.
"""
import os, json, datetime as dt
from collections import defaultdict
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA=os.path.join(ROOT,"data")

C=json.load(open(os.path.join(DATA,"century.json")))
D=json.load(open(os.path.join(DATA,"daily.json")))
M,ORDER=C["meta"],C["order"]
PHASES=C["phases"]

# ---------------- SOURCE A: cited from R1 source spreadsheet ----------------
sourceA={
 "第1年 就職年":     {"winrate":0.58,"avg_ret":"+7%","note":"1950後樣本"},
 "第2年 中期選舉年":  {"winrate":0.58,"avg_ret":"+5%（四年最弱）","note":"年內平均最大回撤~-17%，15次大底落於此年"},
 "第3年 大選前年":    {"winrate":0.95,"avg_ret":"+16.8%（四年最強）","note":"1950後19屆僅1次輕微下跌(2015)"},
 "第4年 大選年":      {"winrate":0.75,"avg_ret":"+7%","note":"前高後震，大頂常見(1972尾/2000/2007)"},
 "黃金3季 Y2Q4→Y3Q2": {"winrate":0.90,"avg_ret":"+20%","note":"16季週期中最肥一段"},
 "中期年低點→其後12個月":{"winrate":1.00,"avg_ret":"+32%","note":"1950後從未失手(15/15)"},
}

# ---------------- SOURCE B1: phase-level P(EASY) across 26 terms ----------------
b1=[]
for ph in PHASES:
    key=ph["key"]
    tot_e=tot_n=0
    for n in ORDER:
        v=C["matrix"][n].get(key)
        if not v: continue
        tot_e+=v["easy"]/100*v["n"]; tot_n+=v["n"]
    if tot_n:
        b1.append({"period":key,"desc":ph["desc"],"winrate":round(tot_e/tot_n,4),
                   "n_terms":sum(1 for n in ORDER if C["matrix"][n].get(key)),"n_days":tot_n})
b1.sort(key=lambda x:-x["winrate"])

# ---------------- SOURCE B2: real NDX month-win-rate, measured window only ----------------
for d in D: d["d"]=dt.date.fromisoformat(d["date"])
D.sort(key=lambda x:x["d"])
PRES_RANGE=[("Obama II","2013-01-20","2017-01-20"),("Trump I","2017-01-20","2021-01-20"),
            ("Biden","2021-01-20","2025-01-20"),("Trump II","2025-01-20","2029-01-20")]
def term_of(dd):
    for n,s,e in PRES_RANGE:
        if dt.date.fromisoformat(s)<=dd<dt.date.fromisoformat(e): return n,dt.date.fromisoformat(s)
    return None,None
for x in D:
    n,ig=term_of(x["d"]); x["term"]=n; x["cd"]=(x["d"]-ig).days if ig else None

# monthly returns (calendar month) tagged with cycle-year (1-4) and phase
months=defaultdict(list)   # (year_or_phase_label) -> list of monthly returns
by_ym=defaultdict(list)
for x in D:
    if x["term"] is None: continue
    ym=(x["d"].year,x["d"].month)
    by_ym[ym].append(x)
monthly=[]
for ym,xs in sorted(by_ym.items()):
    xs.sort(key=lambda z:z["d"])
    ret=xs[-1]["ndx"]/xs[0]["ndx"]-1
    cd=xs[len(xs)//2]["cd"]
    cyear=1 if cd<365 else (2 if cd<730 else (3 if cd<1095 else 4))
    phase=None
    for ph in PHASES:
        if ph["start"]<=cd<ph["end"]: phase=ph["key"]; break
    monthly.append({"ym":ym,"ret":ret,"cyear":cyear,"phase":phase,"term":xs[0]["term"]})

def winrate(items,key,val):
    sub=[m for m in items if m[key]==val]
    if not sub: return None
    wins=sum(1 for m in sub if m["ret"]>0)
    return {"winrate":round(wins/len(sub),4),"n_months":len(sub),
            "avg_ret":round(sum(m["ret"] for m in sub)/len(sub)*100,1)}

b2_year=[]
for cy in (1,2,3,4):
    r=winrate(monthly,"cyear",cy)
    if r: b2_year.append({"period":f"第{cy}年","**":r})
b2_phase=[]
for ph in PHASES:
    r=winrate(monthly,"phase",ph["key"])
    if r: b2_phase.append({"period":ph["key"],"desc":ph["desc"],**r})
b2_phase.sort(key=lambda x:-x["winrate"])

out={"sourceA_R1_cited":sourceA,
     "sourceB1_phase_easy_probability_26terms":b1,
     "sourceB2_real_ndx_monthly_winrate":{"by_cycle_year":[{"period":x["period"],**x["**"]} for x in b2_year],
                                           "by_phase":b2_phase,
                                           "n_months_total":len(monthly),
                                           "window":"2016-07 → 2026-07 (Obama II tail + Trump I + Biden + Trump II)"}}
json.dump(out, open(os.path.join(DATA,"winrate.json"),"w"), ensure_ascii=False, indent=1)

print("=== SOURCE A (R1 cited, S&P500 1950-2024) ===")
for k,v in sorted(sourceA.items(),key=lambda kv:-kv[1]["winrate"]):
    print(f"  {v['winrate']*100:5.1f}%  {k:24s} {v['avg_ret']:16s} {v['note']}")

print("\n=== SOURCE B1 (26-term phase P(EASY), full 100yr reconstruction) ===")
for x in b1:
    print(f"  {x['winrate']*100:5.1f}%  {x['period']:20s} {x['desc']:14s} n_terms={x['n_terms']:2d} n_days={x['n_days']}")

print("\n=== SOURCE B2a (real NDX monthly win-rate BY CYCLE YEAR, measured 2016-2026) ===")
for x in b2_year:
    r=x["**"]
    print(f"  {r['winrate']*100:5.1f}%  {x['period']:10s} avg_ret={r['avg_ret']:+.1f}%  n_months={r['n_months']}")

print("\n=== SOURCE B2b (real NDX monthly win-rate BY PHASE, measured 2016-2026) ===")
for x in b2_phase:
    print(f"  {x['winrate']*100:5.1f}%  {x['period']:20s} {x['desc']:14s} avg_ret={x['avg_ret']:+.1f}%  n_months={x['n_months']}")
