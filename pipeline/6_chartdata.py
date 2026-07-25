import os as _os
_ROOT=_os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
_DATA=_os.path.join(_ROOT,"data")
_SRC=_os.path.join(_ROOT,"source")
import json, datetime
D = json.load(open(_os.path.join(_DATA,"daily.json")))
for d in D: d['d']=datetime.date.fromisoformat(d['date'])
PRES=[("Obama II","2013-01-20","2017-01-20"),("Trump I","2017-01-20","2021-01-20"),
      ("Biden","2021-01-20","2025-01-20"),("Trump II","2025-01-20","2029-01-20")]
def term(dt):
    for name,s,e in PRES:
        if datetime.date.fromisoformat(s)<=dt<datetime.date.fromisoformat(e): return name
    return None
for d in D: d['pres']=term(d['d'])
# per-president daily NDX line (full, compact) + zone per day
out={}
for name,s,e in PRES:
    sub=[d for d in D if d['pres']==name]
    if not sub: continue
    out[name]=[{'t':d['date'],'n':round(d['ndx'],1),'z':d['zone'][0]} for d in sub]  # z = E/U/H
json.dump(out, open(_os.path.join(_DATA,"chartdata.json"),'w'), separators=(',',':'))
tot=sum(len(v) for v in out.values())
print("chart points total:", tot)
for k,v in out.items(): print(f"  {k}: {len(v)} pts  {v[0]['t']}→{v[-1]['t']}  NDX {v[0]['n']}→{v[-1]['n']}")
print("size KB:", round(len(open(_os.path.join(_DATA,"chartdata.json")).read())/1024,1))
