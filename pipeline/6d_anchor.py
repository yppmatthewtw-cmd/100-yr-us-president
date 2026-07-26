# -*- coding: utf-8 -*-
"""R2 (現任錨定版) — project all 26 terms onto the CURRENT president's real calendar.

Anchor = Trump II:
  YEAR 0  當選        2024-11-05
  YEAR 1  就職        2025-01-20  (cd = 0)
  YEAR 2              2026 (calendar year)
  YEAR 3              2027
  YEAR 4              2028
  YEAR 5  卸任        2029-01-20  (cd = 1461)

Every predecessor is aligned by cycle-day (days from own inauguration) and can then be
read off the anchor's real dates.  For every term we emit:
  - zones:        merged regime runs (same MINRUN=4 smoothing as the century heatmap)
  - transitions:  every zone change, annotated with the driving reason
                  (Tier A → verified zone_drivers + nearest major event;
                   Tier B → the source segment's documented basis note)
  - at_now:       the term's state at the anchor's "now" cycle-position
"""
import os as _os, json, datetime as dt
_ROOT=_os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
_DATA=_os.path.join(_ROOT,"data")

C=json.load(open(_os.path.join(_DATA,"century.json")))
segsA=json.load(open(_os.path.join(_DATA,"segments.json")))
ENR={p["name"]:p for p in json.load(open(_os.path.join(_DATA,"enriched.json")))["presidents"]}
CYC=json.load(open(_os.path.join(_DATA,"cycle_aligned.json")))

S,M,ORDER,STEP=C["series"],C["meta"],C["order"],C["step"]
PREV={ORDER[i]:ORDER[i-1] for i in range(1,len(ORDER))}

ANCHOR="Trump II"
AIG=dt.date(2025,1,20); AEL=dt.date(2024,11,5); AEND=dt.date(2029,1,20)
NOW=dt.date(2026,7,10)                      # last data day
CD_NOW=(NOW-AIG).days                       # 536
def ad(cd): return (AIG+dt.timedelta(days=int(cd))).isoformat()

# ---------------- annotation lookups ----------------
def tierA_driver(d):
    """d (ISO) → (president, driver) from the verified smoothed segments + zone_drivers."""
    for pres,slist in segsA.items():
        for sg in slist:
            if sg["start"]<=d<=sg["end"]:
                for zd in ENR.get(pres,{}).get("zone_drivers",[]):
                    if sg["start"] in zd.get("segment",""):
                        return pres,zd["driver"]
                return pres,None
    return None,None

def _evdate(es):
    try:
        if len(es)>=10: return dt.date.fromisoformat(es[:10])
    except ValueError: pass
    try:
        if len(es)>=7: return dt.date.fromisoformat(es[:7]+"-15")
    except ValueError: pass
    return None

def tierA_event(d,win=35):
    dd=dt.date.fromisoformat(d); best=None; bd=win+1
    for pres,e in ENR.items():
        for ev in e.get("events",[]):
            ed=_evdate(ev.get("date",""))
            if not ed: continue
            diff=abs((ed-dd).days)
            if diff<bd: bd=diff; best=ev
    return best

def tierB_note(term,d):
    for sg in M[term]["segs"]:
        if sg["s"]<=d<=sg["e"]: return sg["note"]
    p=PREV.get(term)
    if p:
        for sg in M[p]["segs"]:
            if sg["s"]<=d<=sg["e"]: return f"{sg['note']}（{M[p]['cn']}任內）"
    return None

def annotate(term,pt_tier,d):
    """→ (reason, event_title) for the regime containing date d."""
    if pt_tier=="A":
        pres,drv=tierA_driver(d)
        ev=tierA_event(d)
        return drv or (tierB_note(term,d) or ""), (f"{ev['date']} {ev['title']}" if ev else None)
    return tierB_note(term,d) or "", None

# ---------------- regime runs (same MINRUN merge as century heatmap) ----------------
MINRUN=4
def regime_runs(pts):
    zs=[p["z"] for p in pts]
    def group():
        rs=[]
        for i,z in enumerate(zs):
            if rs and rs[-1]["z"]==z: rs[-1]["b"]=i
            else: rs.append({"z":z,"a":i,"b":i})
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

# ---------------- build every term ----------------
def segZone(d):
    """Official smoothed institutional zone (segments.json) for a Tier-A date."""
    for pres,slist in segsA.items():
        for sg in slist:
            if sg["start"]<=d<=sg["end"]: return sg["zone"][0]
    return None

terms=[]
for n in ORDER:
    m=M[n]
    # Tier-A points: replace the raw weekly-sampled daily zone (which flips day-to-day
    # in the pure-score engine) with the official smoothed institutional segmentation —
    # the anchor view's strips must show regime segments, not sampling noise.
    pts=[]
    for p in S[n]:
        q=dict(p)
        if q.get("tier")=="A":
            z=segZone(q["t"])
            if z: q["z"]=z
        pts.append(q)
    rs=regime_runs(pts)
    zones=[]; trans=[]
    for k,r in enumerate(rs):
        p0,p1=pts[r["a"]],pts[r["b"]]
        pm=pts[(r["a"]+r["b"])//2]
        reason,ev=annotate(n,pm.get("tier"),pm["t"])
        zones.append({"cd0":p0["cd"],"cd1":p1["cd"]+STEP,"z":r["z"],
                      "own0":p0["t"],"own1":p1["t"],"note":reason})
        if k>0:
            t_reason,t_ev=annotate(n,p0.get("tier"),p0["t"])
            trans.append({"cd":p0["cd"],"own":p0["t"],"anchor":ad(p0["cd"]),
                          "frm":rs[k-1]["z"],"to":r["z"],
                          "reason":t_reason,"event":t_ev})
    # at-now snapshot (same cycle position as anchor's now)
    at=None; bd=15
    for p in pts:
        d=abs(p["cd"]-CD_NOW)
        if d<bd: bd=d; at=p
    at_now=({"own":at["t"],"v":at["v"],"z":at["z"]} if at else None)
    tr=C["troughs"].get(n)
    # smoothed index line for the PANE-1 overlay (5-sample centred MA ≈ 5 weeks;
    # Tier-B step data is barely affected, Tier-A weekly sampling noise is damped)
    raw=[p["v"] for p in pts]; line=[]
    for i,p in enumerate(pts):
        a=max(0,i-2); b=min(len(raw),i+3)
        line.append({"cd":p["cd"],"v":round(sum(raw[a:b])/(b-a),1)})
    terms.append({"name":n,"cn":m["cn"],"party":m["party"],"era":m["era"],"tier":m["tier"],
                  "inaug":m["inaug"],"end":m["end"],"election":m["election"],
                  "zones":zones,"transitions":trans,"at_now":at_now,"line":line,
                  "trough":({**tr,"anchor":ad(tr["cd"])} if tr else None)})

# ---------------- anchor-axis furniture ----------------
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
yearbands=[
 {"y":0,"cd0":cdd("2024-11-05"),"cd1":0,"lab":"YEAR 0"},
 {"y":1,"cd0":0,"cd1":cdd("2026-01-01"),"lab":"YEAR 1 · 2025"},
 {"y":2,"cd0":cdd("2026-01-01"),"cd1":cdd("2027-01-01"),"lab":"YEAR 2 · 2026"},
 {"y":3,"cd0":cdd("2027-01-01"),"cd1":cdd("2028-01-01"),"lab":"YEAR 3 · 2027"},
 {"y":4,"cd0":cdd("2028-01-01"),"cd1":cdd("2029-01-01"),"lab":"YEAR 4 · 2028"},
 {"y":5,"cd0":cdd("2029-01-01"),"cd1":1461,"lab":"YEAR 5"},
]

master=CYC["series"].get(ANCHOR,[])   # daily {cd,t,s,sm,z,ix} for the anchor line

# 26-term median at each weekly cycle-day (reference curve on PANE 1)
def _pct(v,q):
    if not v: return None
    s=sorted(v); k=(len(s)-1)*q; f=int(k); c=min(f+1,len(s)-1)
    return round(s[f]+(s[c]-s[f])*(k-f),1)
bycd={}
for T in terms:
    for q in T["line"]: bycd.setdefault(q["cd"],[]).append(q["v"])
median=[{"cd":cd,"med":_pct(v,.5),"n":len(v)} for cd,v in sorted(bycd.items()) if len(v)>=5]

out={"anchor":{"name":ANCHOR,"cn":M[ANCHOR]["cn"],"inaug":AIG.isoformat(),
               "election":AEL.isoformat(),"end":AEND.isoformat(),
               "now":NOW.isoformat(),"cd_now":CD_NOW},
     "milestones":milestones,"yearbands":yearbands,"median":median,
     "master":master,"terms":terms,"step":STEP}
json.dump(out,open(_os.path.join(_DATA,"anchor.json"),"w"),separators=(',',':'),ensure_ascii=False)

print(f"anchor.json written — {len(terms)} terms, cd_now={CD_NOW} ({NOW})")
ntr=sum(len(t["transitions"]) for t in terms)
nno=sum(1 for t in terms for x in t["transitions"] if not x["reason"])
print(f"total transitions: {ntr}  (missing reason: {nno})")
for t in terms[-4:]:
    print(f"\n{t['cn']} at-now: {t['at_now']}")
    for x in t["transitions"][:4]:
        print(f"  {x['own']} {x['frm']}→{x['to']} | {str(x['reason'])[:44]} | ev={str(x['event'])[:40]}")
