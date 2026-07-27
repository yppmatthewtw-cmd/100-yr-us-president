import os as _os
_ROOT=_os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
_DATA=_os.path.join(_ROOT,"data")
_SRC=_os.path.join(_ROOT,"source")
import json, datetime as dt
D = json.load(open(_os.path.join(_DATA,"daily.json")))
for d in D: d['d']=dt.date.fromisoformat(d['date'])
def zone_on(dd):
    cand=[x for x in D if x['d']<=dd]
    return cand[-1] if cand else None
PRES=[("Obama II","2013-01-20"),("Trump I","2017-01-20"),("Biden","2021-01-20"),("Trump II","2025-01-20")]
def elect(y):
    d=dt.date(y,11,1)
    while d.weekday()!=0: d+=dt.timedelta(days=1)
    return d+dt.timedelta(days=1)
KD={}
lo=D[0]['d']; hi=D[-1]['d']
for name,s in PRES:
    inaug=dt.date.fromisoformat(s)
    evs=[("就職 Inauguration",inaug),("首100日 100 Days",inaug+dt.timedelta(days=100)),
         (f"中期選舉 Midterm",elect(inaug.year+1)),(f"大選 Election",elect(inaug.year+3))]
    arr=[]
    for lbl,dd in evs:
        z=zone_on(dd)
        inwin = lo<=dd<=hi
        arr.append({'date':dd.isoformat(),'label':lbl,'zone':(z['zone'] if (z and inwin) else None),
                    'ndx':(round(z['ndx'],0) if (z and inwin) else None),'inwin':inwin})
    KD[name]=arr
json.dump(KD, open(_os.path.join(_DATA,"keydates.json"),'w'), ensure_ascii=False)
print(json.dumps(KD,ensure_ascii=False,indent=1))
