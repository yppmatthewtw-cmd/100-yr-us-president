# -*- coding: utf-8 -*-
"""R4 — extract the COMBINED (A∩B∩C) Easy/Hard index & zone.

Source: EasyHardMoney_NDX_2026R4.5.3_COMBINED_ABC_1.xlsx, sheet 01_整合判區.

The three engines use DIFFERENT thresholds, so raw scores are NOT comparable:
    A  EASY >=70 / HARD <=40        (18 indicators)
    B  EASY >=92 / HARD  <45        ( 5 indicators, fast-layer heavy)
    C  EASY >=80 / HARD  <40        (18 indicators)
Each engine's score is therefore mapped piecewise-linearly onto the canonical
band (its own HARD threshold -> 40, its own EASY threshold -> 70) before use.

整合判區 (zone)  = the file's own unanimity rule (all EASY -> EASY, all HARD ->
                   HARD, otherwise UNCERTAIN). Authoritative; taken verbatim.
整合指數 (index) = a consensus index built to be ALWAYS consistent with that zone:
      consensus EASY  <=>  min(normalised) >= 70   -> index = min  (conviction floor)
      consensus HARD  <=>  max(normalised) <  40   -> index = max  (conviction ceiling)
      otherwise                                    -> index = median, clamped to 41..69
The three normalised engine scores are kept alongside so the dispersion stays visible.
"""
import os as _os, json, datetime as dt
import openpyxl
_ROOT=_os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
_DATA=_os.path.join(_ROOT,"data"); _SRC=_os.path.join(_ROOT,"source")

SRC=_os.path.join(_SRC,"EasyHardMoney_NDX_2026R4.5.3_COMBINED_ABC.xlsx")
TH={"A":(40,70),"B":(45,92),"C":(40,80)}       # (hard_threshold, easy_threshold)

def norm(s,eng):
    """Map an engine score onto the canonical scale: hard_th->40, easy_th->70."""
    if s is None: return None
    h,e=TH[eng]
    if s< h:  return max(0.0, s/h*40) if h else 0.0
    if s< e:  return 40+(s-h)/(e-h)*30
    return min(100.0, 70+(s-e)/(100-e)*30) if e<100 else 100.0

def median3(a,b,c): return sorted([a,b,c])[1]

wb=openpyxl.load_workbook(SRC,data_only=True,read_only=True)
ws=wb["01_整合判區"]
COL={"date":2,"ndx":5,"As":6,"Az":7,"Bs":8,"Bz":9,"Cs":10,"Cz":11,
     "ev":12,"hv":13,"zone":14,"agree":15}
rows=[]
for r in ws.iter_rows(min_row=5,max_row=ws.max_row,values_only=True):
    d=r[COL["date"]-1]
    if d is None: continue
    if isinstance(d,dt.datetime): d=d.date()
    zone=r[COL["zone"]-1]
    if not zone: continue
    A,B,C=r[COL["As"]-1],r[COL["Bs"]-1],r[COL["Cs"]-1]
    nA,nB,nC=norm(A,"A"),norm(B,"B"),norm(C,"C")
    if None in (nA,nB,nC): continue
    lo,hi=min(nA,nB,nC),max(nA,nB,nC)
    if   zone=="EASY": idx=lo
    elif zone=="HARD": idx=hi
    else:              idx=min(69.0,max(41.0,median3(nA,nB,nC)))
    rows.append({"date":d.isoformat(),"ndx":r[COL["ndx"]-1],
                 "zone":zone,"idx":round(idx,1),
                 "ev":r[COL["ev"]-1],"hv":r[COL["hv"]-1],
                 "A":round(nA,1),"B":round(nB,1),"C":round(nC,1),
                 "Araw":A,"Braw":B,"Craw":C,
                 "Az":r[COL["Az"]-1],"Bz":r[COL["Bz"]-1],"Cz":r[COL["Cz"]-1],
                 "spread":round(hi-lo,1)})
json.dump(rows,open(_os.path.join(_DATA,"combined_daily.json"),"w"),
          separators=(',',':'),ensure_ascii=False)

from collections import Counter
c=Counter(x["zone"] for x in rows); n=len(rows)
print(f"combined_daily.json — {n} trading days  {rows[0]['date']} → {rows[-1]['date']}")
for k in ("EASY","UNCERTAIN","HARD"):
    print(f"  {k:10s} {c[k]:5d}  ({c[k]/n*100:.1f}%)")
print(f"  平均分歧度 (三引擎標準化分數 max-min): {sum(x['spread'] for x in rows)/n:.1f}")
print("\n對照 A 引擎單獨: EASY 69.9% / UNC 17.5% / HARD 12.6%")
print("\n整合指數分佈:")
import statistics as st
v=[x["idx"] for x in rows]
print(f"  min {min(v)}  p25 {st.quantiles(v,n=4)[0]:.1f}  median {st.median(v):.1f}  p75 {st.quantiles(v,n=4)[2]:.1f}  max {max(v)}")
# consistency check: index band must match zone
bad=sum(1 for x in rows if (x["zone"]=="EASY")!=(x["idx"]>=70) or (x["zone"]=="HARD")!=(x["idx"]<40))
print(f"  指數與判區一致性檢查: {'OK (0 不一致)' if bad==0 else f'{bad} 筆不一致'}")
