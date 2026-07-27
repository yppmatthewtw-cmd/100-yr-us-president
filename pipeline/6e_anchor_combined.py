# -*- coding: utf-8 -*-
"""R4 — rebuild the anchored dataset with the COMBINED (A∩B∩C) index & zone.

Measured terms (2016-07 → 2026-07) switch from engine A to the 3-engine consensus.
Reconstructed terms (pre-2016) keep their R1-derived segments UNCHANGED — there is
no A/B/C data before 2016, so they cannot be re-derived. Because the Tier-B rubric
was calibrated against engine A (which calls 69.9% of days EASY) while the consensus
calls only 15.7% EASY, cross-tier EASY-share comparison is NOT valid; every term
therefore carries an explicit `standard` field and the report states this up front.
"""
import os as _os, json, datetime as dt
_ROOT=_os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
_DATA=_os.path.join(_ROOT,"data")

CB=json.load(open(_os.path.join(_DATA,"combined_daily.json")))
C =json.load(open(_os.path.join(_DATA,"century.json")))
ENR={p["name"]:p for p in json.load(open(_os.path.join(_DATA,"enriched.json")))["presidents"]}
segsA=json.load(open(_os.path.join(_DATA,"segments.json")))

for d in CB: d["d"]=dt.date.fromisoformat(d["date"])
CB.sort(key=lambda x:x["d"])
CBI={x["date"]:x for x in CB}
DMIN,DMAX=CB[0]["d"],CB[-1]["d"]

S,M,ORDER,STEP=C["series"],C["meta"],C["order"],C["step"]
PREV={ORDER[i]:ORDER[i-1] for i in range(1,len(ORDER))}
ANCHOR="Trump II"
AIG=dt.date(2025,1,20); AEND=dt.date(2029,1,20)
NOW=DMAX; CD_NOW=(NOW-AIG).days
def ad(cd): return (AIG+dt.timedelta(days=int(cd))).isoformat()
def elect_day(y):
    d=dt.date(y,11,1)
    while d.weekday()!=0: d+=dt.timedelta(days=1)
    return d+dt.timedelta(days=1)

# ---------- institutional segments from the COMBINED zone (min 10 trading days) ----------
PRES_RANGE=[(n,dt.date.fromisoformat(M[n]["inaug"]),dt.date.fromisoformat(M[n]["end"]))
            for n in ORDER if not M[n]["segs"] or M[n].get("tier")!="B"]
def term_of(d):
    for n in ORDER:
        if dt.date.fromisoformat(M[n]["inaug"])<=d<dt.date.fromisoformat(M[n]["end"]): return n
    return None

MINDAYS=10
def smooth_segments(days):
    """days: list of dicts with 'zone'. Merge runs shorter than MINDAYS into the larger neighbour."""
    z=[x["zone"] for x in days]
    def group():
        rs=[]
        for i,v in enumerate(z):
            if rs and rs[-1]["z"]==v: rs[-1]["b"]=i
            else: rs.append({"z":v,"a":i,"b":i})
        return rs
    rs=group(); changed=True
    while changed and len(rs)>1:
        changed=False
        for i,r in enumerate(rs):
            if r["b"]-r["a"]+1>=MINDAYS: continue
            L=rs[i-1] if i>0 else None; R=rs[i+1] if i<len(rs)-1 else None
            host=L if (L and (not R or (L["b"]-L["a"])>=(R["b"]-R["a"]))) else R
            if not host: break
            for j in range(r["a"],r["b"]+1): z[j]=host["z"]
            rs=group(); changed=True; break
    return rs

comb_segments={}
byterm={}
for x in CB:
    t=term_of(x["d"])
    if t: byterm.setdefault(t,[]).append(x)
for t,days in byterm.items():
    rs=smooth_segments(days)
    comb_segments[t]=[{"zone":r["z"],"start":days[r["a"]]["date"],"end":days[r["b"]]["date"],
                       "days":r["b"]-r["a"]+1} for r in rs]

# ---------- annotation (narrative describes the market period, not the engine) ----------
def narr_driver(d):
    for pres,slist in segsA.items():
        for sg in slist:
            if sg["start"]<=d<=sg["end"]:
                for zd in ENR.get(pres,{}).get("zone_drivers",[]):
                    if sg["start"] in zd.get("segment",""): return zd["driver"]
    return None
def _evdate(es):
    for fmt in (10,7):
        try: return dt.date.fromisoformat(es[:10] if fmt==10 else es[:7]+"-15")
        except Exception: pass
    return None
def nearest_event(d,win=40):
    dd=dt.date.fromisoformat(d); best=None; bd=win+1
    for e in ENR.values():
        for ev in e.get("events",[]):
            ed=_evdate(ev.get("date",""))
            if not ed: continue
            k=abs((ed-dd).days)
            if k<bd: bd=k; best=ev
    return best
def tierB_note(term,d):
    for sg in M[term]["segs"]:
        if sg["s"]<=d<=sg["e"]: return sg["note"]
    p=PREV.get(term)
    if p:
        for sg in M[p]["segs"]:
            if sg["s"]<=d<=sg["e"]: return f"{sg['note']}（{M[p]['cn']}任內）"
    return None

CD0,CD1=-130,1461
MINRUN=4
def regime_runs(pts):
    zs=[p["z"] for p in pts]
    def group():
        rs=[]
        for i,v in enumerate(zs):
            if rs and rs[-1]["z"]==v: rs[-1]["b"]=i
            else: rs.append({"z":v,"a":i,"b":i})
        return rs
    rs=group(); changed=True
    while changed and len(rs)>1:
        changed=False
        for i,r in enumerate(rs):
            if r["b"]-r["a"]+1>=MINRUN: continue
            L=rs[i-1] if i>0 else None; R=rs[i+1] if i<len(rs)-1 else None
            host=L if (L and (not R or (L["b"]-L["a"])>=(R["b"]-R["a"]))) else R
            if not host: break
            for j in range(r["a"],r["b"]+1): zs[j]=host["z"]
            rs=group(); changed=True; break
    return rs

def combZone(d):
    for t,slist in comb_segments.items():
        for sg in slist:
            if sg["start"]<=d<=sg["end"]: return sg["zone"][0]
    return None

terms=[]
for n in ORDER:
    m=M[n]; ig=dt.date.fromisoformat(m["inaug"])
    isA = any(p.get("tier")=="A" for p in S[n])
    pts=[]
    for p in S[n]:
        q=dict(p)
        if q.get("tier")=="A":
            z=combZone(q["t"])
            if z:
                q["z"]=z
                cbd=CBI.get(q["t"])
                if cbd: q["v"]=cbd["idx"]
        pts.append(q)
    rs=regime_runs(pts)
    zones=[]; trans=[]
    for k,r in enumerate(rs):
        p0,p1,pm=pts[r["a"]],pts[r["b"]],pts[(r["a"]+r["b"])//2]
        isTA=pm.get("tier")=="A"
        reason=(narr_driver(pm["t"]) if isTA else None) or tierB_note(n,pm["t"]) or ""
        zones.append({"cd0":p0["cd"],"cd1":p1["cd"]+STEP,"z":r["z"],
                      "own0":p0["t"],"own1":p1["t"],"note":reason})
        if k>0:
            isT0=p0.get("tier")=="A"
            rea=(narr_driver(p0["t"]) if isT0 else None) or tierB_note(n,p0["t"]) or ""
            ev=nearest_event(p0["t"]) if isT0 else None
            trans.append({"cd":p0["cd"],"own":p0["t"],"anchor":ad(p0["cd"]),
                          "frm":rs[k-1]["z"],"to":r["z"],"reason":rea,
                          "event":(f"{ev['date']} {ev['title']}" if ev else None)})
    at=None; bd=15
    for p in pts:
        k=abs(p["cd"]-CD_NOW)
        if k<bd: bd=k; at=p
    raw=[p["v"] for p in pts]; line=[]
    for i,p in enumerate(pts):
        a=max(0,i-2); b=min(len(raw),i+3)
        line.append({"cd":p["cd"],"v":round(sum(raw[a:b])/(b-a),1)})
    tr=C["troughs"].get(n)
    terms.append({"name":n,"cn":m["cn"],"party":m["party"],"era":m["era"],
                  "tier":m["tier"],"standard":("整合 A∩B∩C" if isA else "重建（A 校準）"),
                  "inaug":m["inaug"],"end":m["end"],"election":m["election"],
                  "zones":zones,"transitions":trans,"line":line,
                  "at_now":({"own":at["t"],"v":at["v"],"z":at["z"]} if at else None),
                  "trough":({**tr,"anchor":ad(tr["cd"])} if tr else None)})

# ---------- master: current president, daily combined ----------
master=[]
cur=[x for x in CB if AIG<=x["d"]<AEND]
def ma(seq,i,w=10):
    a=max(0,i-w); b=min(len(seq),i+w+1)
    return round(sum(seq[a:b])/(b-a),1)
vals=[x["idx"] for x in cur]
vA=[x["A"] for x in cur]; vB=[x["B"] for x in cur]; vC=[x["C"] for x in cur]
for i,x in enumerate(cur):
    master.append({"cd":(x["d"]-AIG).days,"t":x["date"],"s":x["idx"],
                   "sm":ma(vals,i),"z":x["zone"][0],
                   "A":x["A"],"B":x["B"],"C":x["C"],
                   # 21-day MA of each engine, so the three lines are directly
                   # comparable with the (also 21-day MA) combined line
                   "Am":ma(vA,i),"Bm":ma(vB,i),"Cm":ma(vC,i),
                   "ev":x["ev"],"hv":x["hv"],"spread":x["spread"]})

def _pct(v,q):
    s=sorted(v); k=(len(s)-1)*q; f=int(k); c2=min(f+1,len(s)-1)
    return round(s[f]+(s[c2]-s[f])*(k-f),1)
bycd={}
for T in terms:
    for q in T["line"]: bycd.setdefault(q["cd"],[]).append(q["v"])
median=[{"cd":cd,"med":_pct(v,.5),"n":len(v)} for cd,v in sorted(bycd.items()) if len(v)>=5]

def cdd(iso): return (dt.date.fromisoformat(iso)-AIG).days
milestones=[
 {"label":"當選 YEAR 0","date":"2024-11-05","cd":cdd("2024-11-05"),"note":"2024年11月當選"},
 {"label":"就職 YEAR 1","date":"2025-01-20","cd":0,"note":"2025年1月20日就任"},
 {"label":"首100日","date":"2025-04-30","cd":100,"note":"政策開刀窗口（關稅）"},
 {"label":"YEAR 2","date":"2026-01-01","cd":cdd("2026-01-01"),"note":"中期選舉年開始"},
 {"label":"中期選舉","date":"2026-11-03","cd":cdd("2026-11-03"),"note":"2026年11月3日"},
 {"label":"YEAR 3","date":"2027-01-01","cd":cdd("2027-01-01"),"note":"原型最強年"},
 {"label":"YEAR 4","date":"2028-01-01","cd":cdd("2028-01-01"),"note":"大選年"},
 {"label":"大選","date":"2028-11-07","cd":cdd("2028-11-07"),"note":"2028年11月7日"},
 {"label":"卸任 YEAR 5","date":"2029-01-20","cd":1461,"note":"2029年1月20日任滿"},
]

# engine comparison stats over the measured window
from collections import Counter
def share(key):
    c=Counter(x[key] for x in CB); n=len(CB)
    return {k:round(c[k]/n*100,1) for k in ("EASY","UNCERTAIN","HARD")}
engines={"整合 A∩B∩C":share("zone"),"A (Fable)":share("Az"),"B (Sol)":share("Bz"),"C (Grok)":share("Cz")}

out={"anchor":{"name":ANCHOR,"cn":M[ANCHOR]["cn"],"inaug":AIG.isoformat(),
               "election":"2024-11-05","end":AEND.isoformat(),
               "now":NOW.isoformat(),"cd_now":CD_NOW},
     "milestones":milestones,"median":median,"master":master,"terms":terms,"step":STEP,
     "engines":engines,"n_days":len(CB),
     "avg_spread":round(sum(x["spread"] for x in CB)/len(CB),1),
     "comb_segments":comb_segments}
json.dump(out,open(_os.path.join(_DATA,"anchor_combined.json"),"w"),
          separators=(',',':'),ensure_ascii=False)

ntr=sum(len(t["transitions"]) for t in terms)
miss=sum(1 for t in terms for x in t["transitions"] if not x["reason"])
print(f"anchor_combined.json — {len(terms)} terms, {ntr} transitions (missing reason: {miss})")
print("engine zone shares (2016-07→2026-07):")
for k,v in engines.items(): print(f"  {k:14s} EASY {v['EASY']:5.1f}%  UNC {v['UNCERTAIN']:5.1f}%  HARD {v['HARD']:5.1f}%")
print("\ncombined institutional segments per measured term:")
for t,sl in comb_segments.items():
    print(f"  {M[t]['cn']}: {len(sl)} segments")
    for sg in sl: print(f"      {sg['zone']:9s} {sg['start']} → {sg['end']} ({sg['days']}d)")
