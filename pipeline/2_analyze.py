import os as _os
_ROOT=_os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
_DATA=_os.path.join(_ROOT,"data")
_SRC=_os.path.join(_ROOT,"source")
import json, datetime
from collections import Counter, defaultdict
D = json.load(open(_os.path.join(_DATA,"daily.json")))
for d in D:
    d['d']=datetime.date.fromisoformat(d['date'])

# Presidencies covered by data (term start/end). Inauguration Jan 20.
PRES = [
    ("Obama II","2013-01-20","2017-01-20","Democrat"),
    ("Trump I","2017-01-20","2021-01-20","Republican"),
    ("Biden","2021-01-20","2025-01-20","Democrat"),
    ("Trump II","2025-01-20","2029-01-20","Republican"),
]
def term(dt):
    for name,s,e,p in PRES:
        s=datetime.date.fromisoformat(s); e=datetime.date.fromisoformat(e)
        if s<=dt<e: return name
    return None
for d in D: d['pres']=term(d['d'])

# Per-president coverage & zone stats
print("=== PER-PRESIDENT COVERAGE & ZONE % (from daily NDX zone data) ===")
for name,s,e,p in PRES:
    sub=[d for d in D if d['pres']==name]
    if not sub: continue
    c=Counter(d['zone'] for d in sub)
    n=len(sub)
    print(f"\n{name} ({p}): data {sub[0]['date']} → {sub[-1]['date']}  ({n} trading days)")
    print(f"   EASY {c['EASY']} ({c['EASY']/n*100:.1f}%) | UNCERTAIN {c['UNCERTAIN']} ({c['UNCERTAIN']/n*100:.1f}%) | HARD {c['HARD']} ({c['HARD']/n*100:.1f}%)")
    print(f"   NDX {sub[0]['ndx']:.0f} → {sub[-1]['ndx']:.0f}  ({(sub[-1]['ndx']/sub[0]['ndx']-1)*100:+.1f}%)")

# Smoothed regime segmentation: merge runs < MINLEN into neighbors iteratively
def runs(seq):
    out=[]
    for d in seq:
        if out and out[-1]['zone']==d['zone']:
            out[-1]['end']=d; out[-1]['days']+=1
        else:
            out.append({'zone':d['zone'],'start':d,'end':d,'days':1})
    return out

def smooth(seq, minlen=10):
    r=runs(seq)
    changed=True
    while changed and len(r)>1:
        changed=False
        # find shortest run below minlen
        idx=min(range(len(r)), key=lambda i:r[i]['days'])
        if r[idx]['days']>=minlen: break
        # merge idx into the larger neighbor (by days)
        left = r[idx-1] if idx>0 else None
        right= r[idx+1] if idx<len(r)-1 else None
        if left and right:
            tgt = left if left['days']>=right['days'] else right
        else:
            tgt = left or right
        tgt['zone']=tgt['zone']  # keep target zone
        # recompute by relabeling days of idx to tgt zone then re-run
        # Simpler: relabel this run's zone to target's zone, then re-run runs()
        for x in seq:
            if r[idx]['start']['d']<=x['d']<=r[idx]['end']['d']:
                x['szone']=tgt['zone']
        # re-derive using szone
        for x in seq: x.setdefault('szone', x['zone'])
        r=[]
        for d in seq:
            if r and r[-1]['zone']==d['szone']:
                r[-1]['end']=d; r[-1]['days']+=1
            else:
                r.append({'zone':d['szone'],'start':d,'end':d,'days':1})
        changed=True
    return r

# init szone
for d in D: d['szone']=d['zone']
print("\n\n=== SMOOTHED REGIME SEGMENTS (min 10 trading days) PER PRESIDENT ===")
allsegs={}
for name,s,e,p in PRES:
    sub=[d for d in D if d['pres']==name]
    if not sub: continue
    for d in sub: d['szone']=d['zone']
    segs=smooth(sub, minlen=10)
    allsegs[name]=segs
    print(f"\n--- {name} --- ({len(segs)} regimes)")
    for r in segs:
        ndx0=r['start']['ndx']; ndx1=r['end']['ndx']
        # find peak/trough NDX within segment
        seg_days=[d for d in sub if r['start']['d']<=d['d']<=r['end']['d']]
        lo=min(seg_days,key=lambda x:x['ndx']); hi=max(seg_days,key=lambda x:x['ndx'])
        print(f"  {r['zone']:9s} {r['start']['date']} → {r['end']['date']} ({r['days']:3d}d) NDX {ndx0:.0f}→{ndx1:.0f} ({(ndx1/ndx0-1)*100:+.1f}%) | lo {lo['ndx']:.0f}@{lo['date']} hi {hi['ndx']:.0f}@{hi['date']}")

json.dump({name:[{'zone':r['zone'],'start':r['start']['date'],'end':r['end']['date'],'days':r['days'],
                  'ndx_start':r['start']['ndx'],'ndx_end':r['end']['ndx']} for r in segs]
           for name,segs in allsegs.items()},
          open(_os.path.join(_DATA,"segments.json"),'w'), indent=1)
print("\nsaved segments.json")
