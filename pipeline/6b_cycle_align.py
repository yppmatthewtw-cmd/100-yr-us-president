# -*- coding: utf-8 -*-
"""Align every presidency onto ONE consistent presidency-cycle axis.

X = cycle day (days from Inauguration Day = 0; election ≈ -76)
Y = Easy/Hard Index (18-indicator weighted composite score, 0-100;
    >=70 EASY / 40-70 UNCERTAIN / <=40 HARD)

Also produces NDX indexed to 100 at inauguration, on the same axis,
plus a phase x president matrix for the comparison table.
"""
import os as _os, json, datetime as dt
_ROOT=_os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
_DATA=_os.path.join(_ROOT,"data")

D=json.load(open(_os.path.join(_DATA,"daily.json")))
for d in D: d['d']=dt.date.fromisoformat(d['date'])
D.sort(key=lambda x:x['d'])

# ---- presidency definitions (inauguration + preceding election) ----
PRES=[
 {"name":"Obama II","cn":"奧巴馬 II","party":"D","inaug":"2013-01-20","election":"2012-11-06","end":"2017-01-20"},
 {"name":"Trump I", "cn":"特朗普 I", "party":"R","inaug":"2017-01-20","election":"2016-11-08","end":"2021-01-20"},
 {"name":"Biden",   "cn":"拜登",     "party":"D","inaug":"2021-01-20","election":"2020-11-03","end":"2025-01-20"},
 {"name":"Trump II","cn":"特朗普 II","party":"R","inaug":"2025-01-20","election":"2024-11-05","end":"2029-01-20"},
]

def elect_day(y):
    """First Tuesday after the first Monday of November."""
    d=dt.date(y,11,1)
    while d.weekday()!=0: d+=dt.timedelta(days=1)
    return d+dt.timedelta(days=1)

# ---- shared cycle milestones (in cycle days from inauguration) ----
# built from the Trump I calendar as the canonical reference, then rounded
def build_milestones(inaug_year=2017):
    ig=dt.date(inaug_year,1,20)
    ms=[
      ("當選 Election",              (elect_day(inaug_year-1)-ig).days, "選前不確定性出清"),
      ("就職 Inauguration",          0,                                  "蜜月期起點"),
      ("首100日 100 Days",           100,                                "政策開刀窗口"),
      ("第1年終 End Y1",             365,                                "原型 ~+7%"),
      ("中期選舉 Midterm",           (elect_day(inaug_year+1)-ig).days,  "第2年·不確定性出清事件"),
      ("第2年終 End Y2",             730,                                "原型最弱 ~+5% / -17%回撤"),
      ("第3年終 End Y3",             1095,                               "原型最強 ~+16.8%"),
      ("大選 Election",              (elect_day(inaug_year+3)-ig).days,  "第4年·結果落地"),
      ("卸任 End of Term",           1461,                               "交棒"),
    ]
    return [{"label":l,"day":d,"note":n} for l,d,n in ms]
MILESTONES=build_milestones()

# cycle-year phase bands (for background + phase matrix)
PHASES=[
  ("交接期 Transition","當選→就職",  -80,    0),
  ("首100日 First 100d","就職→第100日",0,   100),
  ("第1年 Year 1","第100日→第1年終", 100,   365),
  ("第2年上 Y2 H1","第1年終→中期選舉",365,  658),
  ("第2年下 Y2 H2","中期選舉→第2年終",658,  730),
  ("第3年 Year 3","第2年終→第3年終",  730,  1095),
  ("第4年 Year 4","第3年終→大選",     1095, 1384),
  ("跛腳期 Lame Duck","大選→卸任",    1384, 1461),
]

def smooth(vals, w=21):
    """Centered moving average, shrinking at the edges (no NaN, no phantom flat ends)."""
    n=len(vals); out=[]
    h=w//2
    for i in range(n):
        a=max(0,i-h); b=min(n,i+h+1)
        seg=vals[a:b]
        out.append(sum(seg)/len(seg))
    return out

series={}; meta={}
for p in PRES:
    ig=dt.date.fromisoformat(p['inaug']); en=dt.date.fromisoformat(p['end'])
    el=dt.date.fromisoformat(p['election'])
    # include the transition window (from election day) through end of term
    sub=[d for d in D if el<=d['d']<en]
    if not sub: continue
    # NDX base = close on/just before inauguration (index=100 at inauguration)
    pre=[d for d in sub if d['d']<=ig]
    base=(pre[-1]['ndx'] if pre else sub[0]['ndx'])
    raw=[d['score'] for d in sub]
    sm=smooth(raw,21)
    pts=[]
    for d,sv in zip(sub,sm):
        pts.append({
            "cd": (d['d']-ig).days,            # cycle day
            "t":  d['date'],
            "s":  round(d['score'],1),          # raw Easy/Hard Index
            "sm": round(sv,1),                  # 21d smoothed
            "z":  d['zone'][0],
            "ix": round(d['ndx']/base*100,2),   # NDX indexed, inauguration = 100
        })
    series[p['name']]=pts
    meta[p['name']]={**{k:v for k,v in p.items()},
                     "cd_min":pts[0]['cd'],"cd_max":pts[-1]['cd'],
                     "n":len(pts),"ndx_base":round(base,1),
                     "partial": pts[-1]['cd'] < 1400 or pts[0]['cd'] > -60}

# ---- phase x president matrix ----
matrix={}
for name,pts in series.items():
    row={}
    for key,desc,a,b in PHASES:
        seg=[q for q in pts if a<=q['cd']<b]
        if not seg:
            row[key]=None; continue
        n=len(seg)
        ez=sum(1 for q in seg if q['z']=='E'); uz=sum(1 for q in seg if q['z']=='U'); hz=sum(1 for q in seg if q['z']=='H')
        row[key]={
          "avg":round(sum(q['s'] for q in seg)/n,1),
          "min":round(min(q['s'] for q in seg),1),
          "max":round(max(q['s'] for q in seg),1),
          "easy":round(ez/n*100), "unc":round(uz/n*100), "hard":round(hz/n*100),
          "n":n,
          "ndx":round((seg[-1]['ix']/seg[0]['ix']-1)*100,1),
        }
    matrix[name]=row

# ---- cross-president averages per phase (the "archetype" line) ----
archetype={}
for key,desc,a,b in PHASES:
    vals=[matrix[n][key]['avg'] for n in matrix if matrix[n].get(key)]
    ndxs=[matrix[n][key]['ndx'] for n in matrix if matrix[n].get(key)]
    archetype[key]={"avg":round(sum(vals)/len(vals),1) if vals else None,
                    "ndx":round(sum(ndxs)/len(ndxs),1) if ndxs else None,
                    "n_pres":len(vals)}

out={"series":series,"meta":meta,"milestones":MILESTONES,
     "phases":[{"key":k,"desc":d,"start":a,"end":b} for k,d,a,b in PHASES],
     "matrix":matrix,"archetype":archetype}
json.dump(out, open(_os.path.join(_DATA,"cycle_aligned.json"),"w"), separators=(',',':'), ensure_ascii=False)

print("cycle_aligned.json written")
for n,m in meta.items():
    print(f"  {n:9s} cycleDay {m['cd_min']:5d} → {m['cd_max']:5d}  ({m['n']:4d} pts)  base NDX {m['ndx_base']}  partial={m['partial']}")
print("\nphase averages (Easy/Hard Index):")
hdr="  {:16s}".format("phase")+"".join(f"{n:>11s}" for n in series)+f"{'四任平均':>11s}"
print(hdr)
for k,d,a,b in PHASES:
    line="  {:16s}".format(k)
    for n in series:
        v=matrix[n].get(k)
        line+=f"{(str(v['avg']) if v else '—'):>11s}"
    av=archetype[k]['avg']
    line+=f"{(str(av) if av else '—'):>11s}"
    print(line)
