# -*- coding: utf-8 -*-
"""R9 — resolve every score>60 node's fuzzy `when` string to a cycle-day (cd)
relative to the current term's inauguration (2025-01-20 = cd 0), so PANE 1
can plot them as a dedicated layer alongside the existing 9 milestones.
"""
import os, json, re, datetime as dt
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AIG=dt.date(2025,1,20)

R=json.load(open(os.path.join(ROOT,"data","nodes100_scored.json")))
HI=[x for x in R if x["score"]>60]

MID={"初":5,"中":15,"下旬":25,"起":5,"前":-3}

def parse(when):
    w=when.strip()
    # exact date  YYYY-MM-DD
    m=re.fullmatch(r"(\d{4})-(\d{2})-(\d{2})", w)
    if m: return dt.date(int(m[1]),int(m[2]),int(m[3]))
    # date range same month  YYYY-MM-DD/DD
    m=re.fullmatch(r"(\d{4})-(\d{2})-(\d{2})/(\d{2})", w)
    if m: return dt.date(int(m[1]),int(m[2]),int(m[3]))
    # bare YYYY-MM (no suffix) -> mid-month
    m=re.fullmatch(r"(\d{4})-(\d{2})", w)
    if m: return dt.date(int(m[1]),int(m[2]),15)
    # YYYY-MM 中/初/下旬/起/前
    m=re.fullmatch(r"(\d{4})-(\d{2}) ?(\S+)", w)
    if m:
        y,mo,suf=int(m[1]),int(m[2]),m[3]
        d=MID.get(suf,15)
        return dt.date(y,mo,1)+dt.timedelta(days=d-1)
    # YYYY-MM–MM (month range, same year) -> midpoint month, mid-day
    m=re.fullmatch(r"(\d{4})-(\d{2})[–-](\d{2})", w)
    if m:
        y,mo1,mo2=int(m[1]),int(m[2]),int(m[3])
        mid=(mo1+mo2)//2
        return dt.date(y,mid,15)
    # YYYY年中
    m=re.fullmatch(r"(\d{4})-年中", w)
    if m: return dt.date(int(m[1]),7,1)
    # YYYY-QN
    m=re.fullmatch(r"(\d{4})-Q(\d)", w)
    if m:
        y,q=int(m[1]),int(m[2])
        return dt.date(y,(q-1)*3+2,15)
    # YYYY-HN (half-year)
    m=re.fullmatch(r"(\d{4})-H(\d)", w)
    if m:
        y,h=int(m[1]),int(m[2])
        return dt.date(y,3 if h==1 else 9,15)
    # cross-year range  YYYY-MM–YYYY-MM
    m=re.fullmatch(r"(\d{4})-(\d{2})[–-](\d{4})-(\d{2})", w)
    if m:
        d1=dt.date(int(m[1]),int(m[2]),1); d2=dt.date(int(m[3]),int(m[4]),1)
        return d1+(d2-d1)//2
    raise ValueError(f"unparsed when: {w!r}")

out=[]
for x in HI:
    d=parse(x["when"])
    cd=(d-AIG).days
    out.append({**x,"date":d.isoformat(),"cd":cd})
out.sort(key=lambda z:z["cd"])

json.dump(out, open(os.path.join(ROOT,"data","hi_nodes.json"),"w"), ensure_ascii=False, indent=1)
print(f"hi_nodes.json — {len(out)} nodes (score>60), cd range {out[0]['cd']} .. {out[-1]['cd']}")
for x in out[:8]: print(f"  cd={x['cd']:5d} {x['date']} score={x['score']:5.1f} {x['node']}")
print("  ...")
for x in out[-4:]: print(f"  cd={x['cd']:5d} {x['date']} score={x['score']:5.1f} {x['node']}")
