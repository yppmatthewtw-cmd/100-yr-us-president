# -*- coding: utf-8 -*-
"""R2 — extend the unified presidency-cycle comparison to ALL 26 terms, 1925-2029.

Two clearly separated data tiers (never blended silently):

  TIER A  量測級 (2016-07 → 2026-07): the real 18-indicator weighted composite
          score from the NDX daily file. Daily resolution.
  TIER B  重建級 (1925 → 2016-07): regime segments transcribed from R1's own
          per-term EASY/HARD windows, cross-checked against documented market
          history (peak/trough dates, Fed turns, crises). Segment resolution —
          a step function, NOT a fabricated daily series.

TIER B index rubric (so the coding is auditable and reproducible):
   92  極致寬鬆/狂潮   melt-up, Fed pinning rates, QE flood
   84  正常牛市順風    trending bull, policy not fighting it
   72  溫和順風        EASY but late / narrowing
   58  震盪未定        chop, no direction
   45  偏緊震盪        tightening bias, grinding
   30  緊縮/熊市       HARD: policy tightening or bear market
   20  嚴重熊市        major bear (-25%+)
   10  崩潰/系統性危機  crash / systemic breakdown
"""
import os as _os, json, datetime as dt
_ROOT=_os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
_DATA=_os.path.join(_ROOT,"data")

L = {"狂潮":92,"牛市":84,"溫和":72,"震盪":58,"偏緊":45,"緊縮":30,"熊市":20,"崩潰":10}

def E(a,b,lv,note): return {"s":a,"e":b,"v":L[lv],"lv":lv,"note":note}

# ---------------------------------------------------------------- 26 terms
# name, cn, party, inauguration, end, tier-B segments (empty => Tier A daily)
TERMS=[
 dict(name="Coolidge",cn="柯立芝",party="R",inaug="1925-03-04",end="1929-03-04",era="戰前",segs=[
   E("1925-03-04","1926-02-28","牛市","咆哮20年代牛市啟動"),
   E("1926-03-01","1926-05-31","震盪","1926年3月回調（佛州地產泡沫破裂）"),
   E("1926-06-01","1928-12-31","狂潮","信貸與槓桿狂潮；道指四年約 +170%"),
   E("1929-01-01","1929-03-04","牛市","投機頂峰前最後段"),
 ]),
 dict(name="Hoover",cn="胡佛",party="R",inaug="1929-03-04",end="1933-03-04",era="戰前",segs=[
   E("1929-03-04","1929-09-03","震盪","衝頂但貨幣已收緊（9/3 見頂 381）"),
   E("1929-09-04","1929-11-13","崩潰","★1929大崩盤（黑色星期二）；11/13 見 198"),
   E("1929-11-14","1930-04-16","偏緊","熊市反彈 +48% 至 1930/4/17"),
   E("1930-04-17","1932-07-08","崩潰","債務通縮崩潰；1932/7/8 見底 41，累計 -89%"),
   E("1932-07-09","1932-09-07","震盪","見底暴力反彈 +93%"),
   E("1932-09-08","1933-03-04","熊市","銀行危機再探底（1933/2/27）"),
 ]),
 dict(name="FDR I",cn="羅斯福 I",party="D",inaug="1933-03-04",end="1937-01-20",era="戰前",segs=[
   E("1933-03-05","1933-07-18","狂潮","廢金本位＋新政再通脹＝教科書 Easy"),
   E("1933-07-19","1933-10-31","震盪","夏季急回調"),
   E("1933-11-01","1936-12-31","牛市","新政再通脹牛市"),
   E("1937-01-01","1937-01-20","溫和","上調存款準備金前夜"),
 ]),
 dict(name="FDR II",cn="羅斯福 II",party="D",inaug="1937-01-20",end="1941-01-20",era="戰前",segs=[
   E("1937-01-20","1937-03-09","震盪","見頂前（3/10 見頂）"),
   E("1937-03-10","1938-03-31","崩潰","★緊縮失誤：準備金上調＋財政緊縮 → -49%"),
   E("1938-04-01","1938-11-09","牛市","再通脹反彈 +60%（第2年見底樣本）"),
   E("1938-11-10","1939-08-31","震盪","反彈後盤整"),
   E("1939-09-01","1941-01-20","緊縮","歐戰爆發、戰事不利"),
 ]),
 dict(name="FDR III",cn="羅斯福 III",party="D",inaug="1941-01-20",end="1945-01-20",era="戰前",segs=[
   E("1941-01-20","1942-04-28","熊市","開戰潰敗；1942/4/28 見底（第2年樣本）"),
   E("1942-04-29","1945-01-20","狂潮","★Fed 釘住利率＝極致 Easy Money；戰時牛市"),
 ]),
 dict(name="FDR IV/Truman",cn="羅斯福 IV/杜魯門",party="D",inaug="1945-01-20",end="1949-01-20",era="戰後",segs=[
   E("1945-01-20","1946-05-29","牛市","戰勝＋流動性充裕（5/29 見頂）"),
   E("1946-05-30","1946-10-09","熊市","★1946 -27%（第2年樣本）"),
   E("1946-10-10","1949-01-20","偏緊","戰後通脹＋48–49 衰退，長期磨底"),
 ]),
 dict(name="Truman",cn="杜魯門",party="D",inaug="1949-01-20",end="1953-01-20",era="戰後",segs=[
   E("1949-01-20","1949-06-13","偏緊","1949 衰退尾段（6/13 見底）"),
   E("1949-06-14","1950-06-24","牛市","新牛市啟動"),
   E("1950-06-25","1950-07-17","緊縮","韓戰爆發急跌"),
   E("1950-07-18","1952-12-31","牛市","★1951 財政部-Fed 協議＝現代貨幣週期起點"),
   E("1953-01-01","1953-01-20","震盪","韓戰尾段緊縮"),
 ]),
 dict(name="Eisenhower I",cn="艾森豪 I",party="R",inaug="1953-01-20",end="1957-01-20",era="戰後",segs=[
   E("1953-01-20","1953-09-14","緊縮","第1年衰退（9/14 見底）"),
   E("1953-09-15","1956-04-06","狂潮","1954 +45%，戰後大牛"),
   E("1956-04-07","1957-01-20","震盪","加息＋盤整"),
 ]),
 dict(name="Eisenhower II",cn="艾森豪 II",party="R",inaug="1957-01-20",end="1961-01-20",era="戰後",segs=[
   E("1957-01-20","1957-10-22","緊縮","1957 衰退 -21%（10/22 見底）"),
   E("1957-10-23","1959-12-31","牛市","1958–59 復甦牛"),
   E("1960-01-01","1960-10-25","緊縮","1960 衰退（10/25 見底）"),
   E("1960-10-26","1961-01-20","溫和","選後回升"),
 ]),
 dict(name="JFK/LBJ",cn="甘迺迪/詹森",party="D",inaug="1961-01-20",end="1965-01-20",era="戰後",segs=[
   E("1961-01-20","1961-12-12","牛市","蜜月牛市（12/12 見頂）"),
   E("1961-12-13","1962-06-26","熊市","★1962 閃崩 -28%（第2年樣本；6/26 見底）"),
   E("1962-06-27","1962-10-23","偏緊","古巴導彈危機"),
   E("1962-10-24","1965-01-20","牛市","1963–64 牛市"),
 ]),
 dict(name="LBJ",cn="詹森",party="D",inaug="1965-01-20",end="1969-01-20",era="戰後",segs=[
   E("1965-01-20","1966-02-09","牛市","續牛（2/9 見頂）"),
   E("1966-02-10","1966-10-07","熊市","★1966 信貸緊縮 -22%（第2年樣本；10/7 見底）"),
   E("1966-10-08","1968-11-29","牛市","1967–68 反彈（11/29 見頂）"),
   E("1968-11-30","1969-01-20","偏緊","通脹緊縮開始"),
 ]),
 dict(name="Nixon I",cn="尼克遜 I",party="R",inaug="1969-01-20",end="1973-01-20",era="滯脹",segs=[
   E("1969-01-20","1970-05-26","熊市","緊縮 -36%（5/26 見底；第2年樣本）"),
   E("1970-05-27","1970-11-01","震盪","見底修復"),
   E("1970-11-02","1973-01-11","狂潮","★Burns 為連任放水＝『政治性 Easy Money』原型"),
   E("1973-01-12","1973-01-20","溫和","1972 大選年衝頂後"),
 ]),
 dict(name="Nixon II/Ford",cn="尼克遜 II/福特",party="R",inaug="1973-01-20",end="1977-01-20",era="滯脹",segs=[
   E("1973-01-20","1974-12-06","崩潰","★石油禁運＋滯脹 -48%（1974/12 見底）"),
   E("1974-12-07","1976-09-21","牛市","1975 +38%（9/21 見頂）"),
   E("1976-09-22","1977-01-20","震盪","選後盤整"),
 ]),
 dict(name="Carter",cn="卡特",party="D",inaug="1977-01-20",end="1981-01-20",era="滯脹",segs=[
   E("1977-01-20","1978-02-28","偏緊","1977 陰跌"),
   E("1978-03-01","1979-10-05","溫和","名義反彈但通脹升溫"),
   E("1979-10-06","1980-03-27","緊縮","★Volcker 衝擊（第3年例外！通脹壓倒政治週期）"),
   E("1980-03-28","1980-11-28","牛市","大選年反彈"),
   E("1980-11-29","1981-01-20","震盪","選後轉弱"),
 ]),
 dict(name="Reagan I",cn="列根 I",party="R",inaug="1981-01-20",end="1985-01-20",era="大緩和",segs=[
   E("1981-01-20","1982-08-12","熊市","★Volcker 絞殺 -27%（1982/8/12 見底＝最經典中期年樣本）"),
   E("1982-08-13","1983-11-29","狂潮","世代牛市起點"),
   E("1983-11-30","1984-07-24","震盪","1984 盤整"),
   E("1984-07-25","1985-01-20","牛市","重啟升勢"),
 ]),
 dict(name="Reagan II",cn="列根 II",party="R",inaug="1985-01-20",end="1989-01-20",era="大緩和",segs=[
   E("1985-01-20","1987-08-25","狂潮","廣場協議寬鬆（8/25 見頂）"),
   E("1987-08-26","1987-12-04","崩潰","★1987 股災 -34%（第3年例外#2）"),
   E("1987-12-05","1989-01-20","牛市","股災後修復"),
 ]),
 dict(name="Bush 41",cn="老布殊",party="R",inaug="1989-01-20",end="1993-01-20",era="大緩和",segs=[
   E("1989-01-20","1990-07-16","牛市","續牛（7/16 見頂）"),
   E("1990-07-17","1990-10-11","熊市","★海灣戰爭 -20%（第2年樣本；10/11 見底）"),
   E("1990-10-12","1993-01-20","牛市","減息週期"),
 ]),
 dict(name="Clinton I",cn="克林頓 I",party="D",inaug="1993-01-20",end="1997-01-20",era="大緩和",segs=[
   E("1993-01-20","1994-01-31","牛市","蜜月續牛"),
   E("1994-02-01","1994-12-08","偏緊","★1994 債券大屠殺（第2年）；全年磨底"),
   E("1994-12-09","1997-01-20","狂潮","★1995 +34%＝現代最強第3年"),
 ]),
 dict(name="Clinton II",cn="克林頓 II",party="D",inaug="1997-01-20",end="2001-01-20",era="科網",segs=[
   E("1997-01-20","1998-07-17","牛市","續牛（7/17 見頂）"),
   E("1998-07-18","1998-10-08","熊市","★LTCM -19%（第2年樣本；10/8 見底）"),
   E("1998-10-09","2000-03-24","狂潮","★1999 blow-off（第3年衝刺原型）"),
   E("2000-03-25","2001-01-20","緊縮","科網爆破（第4年頂）"),
 ]),
 dict(name="Bush 43 I",cn="小布殊 I",party="R",inaug="2001-01-20",end="2005-01-20",era="科網",segs=[
   E("2001-01-20","2002-10-09","崩潰","★科網熊＋911（第1–2年）；2002/10/9 見底"),
   E("2002-10-10","2003-03-11","偏緊","二次探底、築底"),
   E("2003-03-12","2005-01-20","牛市","減息＋減稅"),
 ]),
 dict(name="Bush 43 II",cn="小布殊 II",party="R",inaug="2005-01-20",end="2009-01-20",era="金融海嘯",segs=[
   E("2005-01-20","2007-10-09","牛市","信貸擴張末期（10/9 見頂）"),
   E("2007-10-10","2008-09-14","緊縮","★信用危機展開（第3–4年例外#3）"),
   E("2008-09-15","2009-01-20","崩潰","雷曼倒閉；系統性崩潰"),
 ]),
 dict(name="Obama I",cn="奧巴馬 I",party="D",inaug="2009-01-20",end="2013-01-20",era="QE",segs=[
   E("2009-01-20","2009-03-09","崩潰","最後一跌（3/9 見底）"),
   E("2009-03-10","2010-04-23","狂潮","QE1 大反彈"),
   E("2010-04-24","2010-08-31","偏緊","QE 空窗＋閃崩（2010/7 見底＝中期年樣本）"),
   E("2010-09-01","2011-04-29","牛市","QE2"),
   E("2011-04-30","2011-10-03","緊縮","債限危機 -19%（10/3 見底）"),
   E("2011-10-04","2013-01-20","牛市","QE3"),
 ]),
 # Obama II: Tier B until the daily file starts, then Tier A
 dict(name="Obama II",cn="奧巴馬 II",party="D",inaug="2013-01-20",end="2017-01-20",era="QE",tierA_from="2016-07-08",segs=[
   E("2013-01-20","2014-12-31","狂潮","QE3 melt-up"),
   E("2015-01-01","2015-05-20","溫和","縮表預期升溫（5/20 見頂）"),
   E("2015-05-21","2016-02-11","緊縮","★人幣貶＋縮表預期（第3年例外#4）；2016/2/11 見底"),
   E("2016-02-12","2016-07-07","溫和","V 型修復"),
 ]),
 dict(name="Trump I",cn="特朗普 I",party="R",inaug="2017-01-20",end="2021-01-20",era="現代",segs=[]),
 dict(name="Biden",cn="拜登",party="D",inaug="2021-01-20",end="2025-01-20",era="現代",segs=[]),
 dict(name="Trump II",cn="特朗普 II",party="R",inaug="2025-01-20",end="2029-01-20",era="現代",segs=[]),
]

def elect_day(y):
    d=dt.date(y,11,1)
    while d.weekday()!=0: d+=dt.timedelta(days=1)
    return d+dt.timedelta(days=1)

# ---------------------------------------------------------------- Tier A daily
DAILY=json.load(open(_os.path.join(_DATA,"daily.json")))
for d in DAILY: d["d"]=dt.date.fromisoformat(d["date"])
DAILY.sort(key=lambda x:x["d"])
DMIN,DMAX=DAILY[0]["d"],DAILY[-1]["d"]

STEP=7           # sample the shared cycle axis weekly
CD0,CD1=-130,1461

# every term's own segments, parsed once — the transition window (cd<0) of term N
# is covered by term N-1's segments, since the terms are contiguous.
ALLSEGS={T["name"]:[{**s,"sd":dt.date.fromisoformat(s["s"]),"ed":dt.date.fromisoformat(s["e"])}
                    for s in T["segs"]] for T in TERMS}
PREV={TERMS[i]["name"]: TERMS[i-1]["name"] for i in range(1,len(TERMS))}

series={}; meta={}
for T in TERMS:
    ig=dt.date.fromisoformat(T["inaug"]); en=dt.date.fromisoformat(T["end"])
    el=elect_day(ig.year-1)
    tierA_from = dt.date.fromisoformat(T["tierA_from"]) if T.get("tierA_from") else (DMIN if not T["segs"] else None)
    segs=ALLSEGS[T["name"]]
    prevsegs=ALLSEGS.get(PREV.get(T["name"],""),[])
    pts=[]
    for cd in range(CD0, CD1+1, STEP):
        day = ig + dt.timedelta(days=cd)
        if day < el or day >= en: continue
        val=None; tier=None; note=None
        if tierA_from and day>=tierA_from and DMIN<=day<=DMAX:
            cand=[x for x in DAILY if x["d"]<=day]
            if cand and (day-cand[-1]["d"]).days<=7:
                val=cand[-1]["score"]; tier="A"; note=None
        if val is None:
            pool = segs if day>=ig else (prevsegs+segs)   # cd<0 → outgoing president's term
            for s in pool:
                if s["sd"]<=day<=s["ed"]:
                    val=s["v"]; tier="B"; note=s["note"]; break
        if val is None: continue
        pts.append({"cd":cd,"t":day.isoformat(),"v":round(val,1),"tier":tier,
                    "z":("E" if val>=70 else ("H" if val<=40 else "U"))})
    if not pts: continue
    series[T["name"]]=pts
    nA=sum(1 for p in pts if p["tier"]=="A")
    meta[T["name"]]={"cn":T["cn"],"party":T["party"],"era":T["era"],"inaug":T["inaug"],"end":T["end"],
                     "election":el.isoformat(),"cd_election":(el-ig).days,
                     "tier":("A" if nA==len(pts) else ("混合" if nA else "B")),
                     "n":len(pts),"pctA":round(nA/len(pts)*100),
                     "segs":[{"s":s["s"],"e":s["e"],"lv":s["lv"],"v":s["v"],"note":s["note"]} for s in T["segs"]],
                     "cd_min":pts[0]["cd"],"cd_max":pts[-1]["cd"],
                     "partial": pts[-1]["cd"] < 1400}

ORDER=[T["name"] for T in TERMS if T["name"] in series]

# ---------------------------------------------------------------- archetype envelope
def pct(vals,q):
    if not vals: return None
    v=sorted(vals); k=(len(v)-1)*q; f=int(k); c=min(f+1,len(v)-1)
    return round(v[f]+(v[c]-v[f])*(k-f),1)
envelope=[]
for cd in range(CD0, CD1+1, STEP):
    vals=[]
    for n in ORDER:
        for p in series[n]:
            if p["cd"]==cd: vals.append(p["v"]); break
    if len(vals)<5: continue
    envelope.append({"cd":cd,"n":len(vals),"med":pct(vals,.5),
                     "p25":pct(vals,.25),"p75":pct(vals,.75),
                     "hardpct":round(sum(1 for v in vals if v<=40)/len(vals)*100)})

# ---------------------------------------------------------------- phase matrix
PHASES=[("交接期 Transition","當選→就職",-130,0),("首100日 First 100d","就職→第100日",0,100),
        ("第1年 Year 1","第100日→第1年終",100,365),("第2年上 Y2 H1","第1年終→中期選舉",365,658),
        ("第2年下 Y2 H2","中期選舉→第2年終",658,730),("第3年 Year 3","第2年終→第3年終",730,1095),
        ("第4年 Year 4","第3年終→大選",1095,1384),("跛腳期 Lame Duck","大選→卸任",1384,1462)]
matrix={}
for n in ORDER:
    row={}
    for k,desc,a,b in PHASES:
        seg=[p for p in series[n] if a<=p["cd"]<b]
        if not seg: row[k]=None; continue
        row[k]={"avg":round(sum(p["v"] for p in seg)/len(seg),1),
                "hard":round(sum(1 for p in seg if p["z"]=="H")/len(seg)*100),
                "easy":round(sum(1 for p in seg if p["z"]=="E")/len(seg)*100),"n":len(seg)}
    matrix[n]=row
phase_summary={}
for k,desc,a,b in PHASES:
    vals=[matrix[n][k]["avg"] for n in ORDER if matrix[n].get(k)]
    hs=[matrix[n][k]["hard"] for n in ORDER if matrix[n].get(k)]
    nhard=sum(1 for n in ORDER if matrix[n].get(k) and matrix[n][k]["avg"]<=40)
    phase_summary[k]={"desc":desc,"avg":round(sum(vals)/len(vals),1) if vals else None,
                      "med":pct(vals,.5),"min":min(vals) if vals else None,"max":max(vals) if vals else None,
                      "terms":len(vals),"terms_hard":nhard,
                      "hardday":round(sum(hs)/len(hs)) if hs else None}

# ---------------------------------------------------------------- cycle-year stats
YEARS=[("第1年 就職年",0,365),("第2年 中期選舉年",365,730),("第3年 大選前年",730,1095),("第4年 大選年",1095,1461)]
yearstats={}
for lbl,a,b in YEARS:
    per={}
    for n in ORDER:
        seg=[p for p in series[n] if a<=p["cd"]<b]
        if len(seg)>=20: per[n]=round(sum(p["v"] for p in seg)/len(seg),1)
    vals=list(per.values())
    yearstats[lbl]={"per":per,"avg":round(sum(vals)/len(vals),1),"med":pct(vals,.5),
                    "terms":len(vals),"hard_terms":sum(1 for v in vals if v<=40),
                    "easy_terms":sum(1 for v in vals if v>=70),
                    "worst":min(per,key=per.get),"worst_v":min(vals),
                    "best":max(per,key=per.get),"best_v":max(vals)}

# ---------------------------------------------------------------- trough location
# NOTE: deriving the trough from the Tier-B step function is invalid — a HARD block's
# minimum ties across its whole span and resolves to its START, not the real bottom.
# So the bottoms below are DOCUMENTED closing-low dates, not derived from the index.
# TERM_LOW = the term's own major low.  MIDTERM_LOW = R1's 15 中期選舉年大底 samples.
TERM_LOW={
 "Coolidge":("1926-03-30","1926年3月回調低點（任內無大型底部）"),
 "Hoover":("1932-07-08","道指 41.22，自 1929 高點 -89%"),
 "FDR I":("1933-10-21","1933 夏季回調低點"),
 "FDR II":("1938-03-31","緊縮失誤熊市底 -49%"),
 "FDR III":("1942-04-28","二戰潰敗段底部"),
 "FDR IV/Truman":("1946-10-09","1946 -27% 底"),
 "Truman":("1949-06-13","1949 衰退底"),
 "Eisenhower I":("1953-09-14","第1年衰退底"),
 "Eisenhower II":("1957-10-22","1957 衰退 -21% 底"),
 "JFK/LBJ":("1962-06-26","1962 閃崩 -28% 底"),
 "LBJ":("1966-10-07","1966 信貸緊縮 -22% 底"),
 "Nixon I":("1970-05-26","1969-70 緊縮 -36% 底"),
 "Nixon II/Ford":("1974-12-06","石油禁運熊市 -48% 底"),
 "Carter":("1980-03-27","Volcker 衝擊後底"),
 "Reagan I":("1982-08-12","Volcker 絞殺底＝世代牛市起點"),
 "Reagan II":("1987-12-04","1987 股災 -34% 底"),
 "Bush 41":("1990-10-11","海灣戰爭 -20% 底"),
 "Clinton I":("1994-12-08","1994 債券大屠殺磨底"),
 "Clinton II":("1998-10-08","LTCM -19% 底"),
 "Bush 43 I":("2002-10-09","科網熊市底"),
 "Bush 43 II":("2008-11-20","雷曼後任內低點（真正底 2009-03-09 落在下任）"),
 "Obama I":("2009-03-09","金融海嘯總底"),
 "Obama II":("2016-02-11","縮表預期+人幣貶底"),
 "Trump I":("2018-12-24","加息+QT 底 -23%"),
 "Biden":("2022-12-28","NDX 加息熊市底 -35%"),
 "Trump II":("2025-04-08","關稅崩盤底 -23%（任期進行中）"),
}
# R1 明列的 15 次「大級別底部落在第2年（中期選舉年）」樣本
MIDTERM_LOW={
 "FDR II":"1938-03-31","FDR III":"1942-04-28","FDR IV/Truman":"1946-10-09",
 "JFK/LBJ":"1962-06-26","LBJ":"1966-10-07","Nixon I":"1970-05-26",
 "Nixon II/Ford":"1974-12-06","Reagan I":"1982-08-12","Bush 41":"1990-10-11",
 "Clinton I":"1994-12-08","Clinton II":"1998-10-08","Bush 43 I":"2002-10-09",
 "Obama I":"2010-07-02","Trump I":"2018-12-24","Biden":"2022-12-28",
}

def cyc_year(cd):
    if cd<0: return "交接期"
    return ["第1年","第2年","第3年","第4年"][min(3,cd//365)]

troughs={}; ydist={"交接期":0,"第1年":0,"第2年":0,"第3年":0,"第4年":0}
for n in ORDER:
    if n not in TERM_LOW: continue
    ds,note=TERM_LOW[n]
    ig=dt.date.fromisoformat(meta[n]["inaug"])
    cd=(dt.date.fromisoformat(ds)-ig).days
    yb=cyc_year(cd)
    troughs[n]={"date":ds,"cd":cd,"year":yb,"month":int(ds[5:7]),"note":note,
                "midterm_low":MIDTERM_LOW.get(n)}
    ydist[yb]+=1
mdist={m:0 for m in range(1,13)}
for v in troughs.values(): mdist[v["month"]]+=1
# month distribution of R1's 15 midterm-year lows
mt_m={m:0 for m in range(1,13)}
for d in MIDTERM_LOW.values(): mt_m[int(d[5:7])]+=1
midterm_stats={"n":len(MIDTERM_LOW),"of_terms":len(ORDER),"months":mt_m,
               "aug_oct":sum(mt_m[m] for m in (8,9,10)),
               "q4":sum(mt_m[m] for m in (10,11,12)),
               "dec":mt_m[12],
               "list":[{"term":k,"date":v,"year":int(v[:4])} for k,v in MIDTERM_LOW.items()]}

out={"troughs":troughs,"trough_year_dist":ydist,"trough_month_dist":mdist,"midterm":midterm_stats,
     "series":series,"meta":meta,"order":ORDER,"envelope":envelope,
     "phases":[{"key":k,"desc":d,"start":a,"end":b} for k,d,a,b in PHASES],
     "matrix":matrix,"phase_summary":phase_summary,"yearstats":yearstats,
     "rubric":L,"step":STEP,
     "milestones":[{"label":"當選 Election","day":-76,"note":"選前不確定性出清（1937前為 3/4 就職，約 -120 日）"},
                   {"label":"就職 Inauguration","day":0,"note":"蜜月期起點"},
                   {"label":"首100日 100 Days","day":100,"note":"政策開刀窗口"},
                   {"label":"第1年終 End Y1","day":365,"note":"原型 ~+7%"},
                   {"label":"中期選舉 Midterm","day":655,"note":"第2年·不確定性出清事件"},
                   {"label":"第2年終 End Y2","day":730,"note":"原型最弱 ~+5% / -17%回撤"},
                   {"label":"第3年終 End Y3","day":1095,"note":"原型最強 ~+16.8%"},
                   {"label":"大選 Election","day":1383,"note":"第4年·結果落地"},
                   {"label":"卸任 End of Term","day":1461,"note":"交棒"}]}
json.dump(out, open(_os.path.join(_DATA,"century.json"),"w"), separators=(',',':'), ensure_ascii=False)

print(f"century.json written — {len(ORDER)} terms, envelope {len(envelope)} pts\n")
print("Tier coverage:")
for n in ORDER:
    m=meta[n]
    print(f"  {n:16s} {m['inaug'][:4]}-{m['end'][:4]}  tier={m['tier']:3s} A={m['pctA']:3d}%  pts={m['n']}")
print("\n=== 週期階段（26 屆彙總）===")
print(f"  {'階段':18s}{'平均':>7s}{'中位':>7s}{'最低':>7s}{'HARD屆數':>10s}{'HARD日佔':>9s}")
for k,d,a,b in PHASES:
    s=phase_summary[k]
    print(f"  {k:18s}{s['avg']:>7.1f}{s['med']:>7.1f}{s['min']:>7.1f}{str(s['terms_hard'])+'/'+str(s['terms']):>10s}{str(s['hardday'])+'%':>9s}")
print("\n=== 各任『任內最大底部』落在哪一個週期年（26 屆, 依實際見底日）===")
for k,v in ydist.items():
    if v: print(f"  {k}: {v} 屆  ({v/len(troughs)*100:.0f}%)")
print("  月份分佈:", " ".join(f"{m}月×{c}" for m,c in mdist.items() if c))
print(f"\n=== R1『大級別底部落在第2年（中期選舉年）』的 {midterm_stats['n']} 次樣本 ===")
print(f"  {midterm_stats['n']}/{midterm_stats['of_terms']} 屆 = {midterm_stats['n']/midterm_stats['of_terms']*100:.0f}%")
print("  月份:", " ".join(f"{m}月×{c}" for m,c in mt_m.items() if c))
print(f"  8–10月 {midterm_stats['aug_oct']}/{midterm_stats['n']} | Q4(10-12月) {midterm_stats['q4']}/{midterm_stats['n']} | 12月 {midterm_stats['dec']}/{midterm_stats['n']}")
print("\n=== 總統週期年（26 屆）===")
for lbl,a,b in YEARS:
    y=yearstats[lbl]
    print(f"  {lbl:14s} 平均 {y['avg']:5.1f} | 中位 {y['med']:5.1f} | HARD屆 {y['hard_terms']:2d}/{y['terms']:2d} | "
          f"最差 {y['worst']}({y['worst_v']}) | 最佳 {y['best']}({y['best_v']})")
