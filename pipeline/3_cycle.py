import os as _os
_ROOT=_os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
_DATA=_os.path.join(_ROOT,"data")
_SRC=_os.path.join(_ROOT,"source")
import json, datetime
from collections import Counter
D = json.load(open(_os.path.join(_DATA,"daily.json")))
for d in D: d['d']=datetime.date.fromisoformat(d['date'])
PRES=[("Obama II","2013-01-20","2017-01-20"),("Trump I","2017-01-20","2021-01-20"),
      ("Biden","2021-01-20","2025-01-20"),("Trump II","2025-01-20","2029-01-20")]
def term(dt):
    for name,s,e in PRES:
        if datetime.date.fromisoformat(s)<=dt<datetime.date.fromisoformat(e): return name,int(s[:4])
    return None,None
for d in D:
    d['pres'],d['inaug']=term(d['d'])

# cycle year = calendar year - inauguration year + 1
print("=== PER CYCLE-YEAR ZONE% + NDX RETURN + MAX DRAWDOWN (empirical NDX) ===")
print("R1 baseline: Y1~+7%/honeymoon | Y2~+5% weakest, -17% avg DD, midterm bottom | Y3~+16.8% strongest | Y4~+7%")
out={}
for name,s,e in PRES:
    sub=[d for d in D if d['pres']==name]
    if not sub: continue
    inaug=int(s[:4])
    print(f"\n### {name} (inaug {inaug}) ###")
    byyear={}
    for cy in range(1,5):
        cal=inaug+cy-1
        yd=[d for d in sub if d['d'].year==cal]
        if not yd: continue
        c=Counter(d['zone'] for d in yd); n=len(yd)
        ret=(yd[-1]['ndx']/yd[0]['ndx']-1)*100
        # max drawdown within year (peak to trough after peak)
        peak=-1; maxdd=0; peakd=trod=None; runpeak=yd[0]['ndx']; rpd=yd[0]
        for d in yd:
            if d['ndx']>runpeak: runpeak=d['ndx']; rpd=d
            dd=(d['ndx']/runpeak-1)*100
            if dd<maxdd: maxdd=dd; peakd=rpd; trod=d
        lbl={1:'Y1 就職年',2:'Y2 中期選舉年',3:'Y3 大選前年',4:'Y4 大選年'}[cy]
        partial=" (partial)" if len(yd)<200 and cal>=2026 else ""
        print(f"  {lbl} [{cal}]{partial}: {n}d | EASY {c['EASY']/n*100:.0f}% UNC {c['UNCERTAIN']/n*100:.0f}% HARD {c['HARD']/n*100:.0f}% | NDXret {ret:+.1f}% | maxDD {maxdd:.1f}%" + (f" (peak {peakd['date']}→trough {trod['date']})" if maxdd<-3 else ""))
        byyear[cy]={'cal':cal,'n':n,'easy':c['EASY']/n,'unc':c['UNCERTAIN']/n,'hard':c['HARD']/n,'ret':ret,'maxdd':maxdd,
                    'peak':peakd['date'] if peakd else None,'trough':trod['date'] if trod else None,'label':lbl}
    out[name]={'inaug':inaug,'years':byyear}
json.dump(out, open(_os.path.join(_DATA,"cycleyears.json"),'w'), indent=1)

# Key dates per president
print("\n\n=== KEY DATES (with zone on/around that date) ===")
def zone_on(dt):
    # nearest trading day <= dt
    cand=[d for d in D if d['d']<=dt]
    return cand[-1] if cand else None
import datetime as dt2
for name,s,e in PRES:
    inaug=datetime.date.fromisoformat(s)
    print(f"\n{name}:")
    events=[("就職 Inauguration", inaug),
            ("首100日 First 100 days", inaug+dt2.timedelta(days=100))]
    # midterm election year2 Nov, presidential year4 Nov
    y2=inaug.year+1; y4=inaug.year+3
    # first Tue after first Mon of Nov
    def elect(y):
        d=datetime.date(y,11,1)
        while d.weekday()!=0: d+=dt2.timedelta(days=1)  # first Monday
        return d+dt2.timedelta(days=1)
    events.append((f"中期選舉 Midterm ({y2})", elect(y2)))
    events.append((f"大選 Presidential ({y4})", elect(y4)))
    for lbl,dd in events:
        z=zone_on(dd)
        if z and z['d']<=datetime.date.fromisoformat('2026-07-10') and z['d']>=datetime.date.fromisoformat('2016-07-08'):
            print(f"   {dd.isoformat()} {lbl:32s} → zone {z['zone']:9s} NDX {z['ndx']:.0f} (as of {z['date']})")
        else:
            print(f"   {dd.isoformat()} {lbl:32s} → (outside data window)")
