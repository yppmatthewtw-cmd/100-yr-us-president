# -*- coding: utf-8 -*-
"""Score all 100 recurring cycle-nodes on an auditable 4-dimension model.

Every node gets four 1-5 sub-scores; the weighted sum is rescaled to 0-100.

  M 市場衝擊力 (Market impact)      ×0.40  該節點歷史上直接改變 E/H 判區的能力
  I 不可迴避性 (Inevitability)      ×0.20  是否憲法/法定日曆（無法延期/取消）
  P 政策不可逆性 (Policy bindingness)×0.20  當日決定是否鎖死後續數月路徑
  E 實證支持度 (Evidence)           ×0.20  本 repo 26 屆數據對其重要性的支持強度

Sub-scores are assigned per node below; the arithmetic is deterministic so any
reader can re-derive or challenge a single dimension without touching the rest.
"""
import os, json
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
N=json.load(open(os.path.join(ROOT,"data","nodes100.json")))

W={"M":0.40,"I":0.20,"P":0.20,"E":0.20}

# node name (exact) -> (M, I, P, E)
S={
 # ---- YEAR 0 ----
 "大選日":(5,5,5,5),
 "選後首個 FOMC":(4,4,4,3),
 "內閣人事提名潮":(3,3,3,2),
 "12月 FOMC＋點陣圖|Y0":(5,4,5,4),
 "12月 FOMC＋點陣圖|Y2":(5,4,5,5),
 "選舉人團投票":(1,5,1,1),
 "新一屆國會就任":(2,5,3,2),
 "國會認證選舉結果":(2,5,1,1),
 "就職日（週期第0日）":(4,5,5,5),
 # ---- YEAR 1 ----
 "首週行政命令潮":(4,3,4,4),
 "1月 FOMC":(3,4,3,3),
 "內閣確認聽證季":(2,3,2,2),
 "Fed 主席半年度證詞（參眾兩院）":(3,5,3,3),
 "首次國會聯席演說（準國情咨文）":(2,4,3,2),
 "首份預算綱要":(4,4,5,4),
 "3月 FOMC＋點陣圖":(4,4,4,4),
 "報稅日":(3,5,2,3),
 "首100日":(4,3,4,5),
 "5月 FOMC":(3,4,3,2),
 "G7 峰會＋外交季（9月聯大）":(2,3,2,2),
 "6月 FOMC＋點陣圖":(4,4,4,4),
 "債務上限 X-date 窗口":(5,3,4,5),
 "Fed 主席證詞":(3,5,3,3),
 "7月 FOMC":(3,4,3,2),
 "國會夏休前立法衝刺":(3,3,4,2),
 "Jackson Hole 年會":(4,3,4,4),
 "9月 FOMC＋點陣圖|Y1":(4,4,4,4),
 "9月 FOMC＋點陣圖|Y2":(5,4,5,5),
 "財政年度開始／停擺風險":(4,5,3,4),
 "10月 FOMC":(3,4,3,2),
 "外圍選舉風向標（VA/NJ 州長）":(2,3,1,2),
 "12月 FOMC＋點陣圖|Y1":(4,4,4,3),
 "NDAA／年末支出案":(2,4,3,2),
 "第1年收官":(3,5,2,4),
 # ---- YEAR 2 ----
 "國情咨文":(2,4,3,2),
 "Y2 Hard 高發段開啟（2–9月）":(5,3,3,5),
 "預算案":(3,4,4,3),
 "中期初選季":(2,3,2,2),
 "Fed 主席任期屆滿節點":(5,4,5,5),
 "Jackson Hole":(4,3,4,4),
 "Y2 大底歷史窗口開啟":(5,3,3,5),
 "財政年度開始／選前停擺博弈":(4,5,3,4),
 "中期選舉日":(5,5,5,5),
 "選後出清反彈窗":(4,4,2,5),
 "跛腳鴨國會年末會期":(3,4,4,3),
 "Y2 大底確認節點":(5,3,3,5),
 "黃金三季起點（Y2Q4→Y3Q2）":(5,3,3,5),
 # ---- YEAR 3 ----
 "新國會就任（中期結果生效）":(3,5,4,3),
 "政治托市窗口全開":(5,3,4,5),
 "債務上限再現窗口":(4,3,4,4),
 "對手黨初選陣營成形":(2,3,2,2),
 "Y3 收官":(4,5,2,5),
 # ---- YEAR 4 ----
 "國情咨文（選舉年版）":(2,4,2,2),
 "初選季開跑（Iowa/NH）":(2,4,2,2),
 "超級星期二":(3,4,3,3),
 "兩黨全國代表大會":(3,4,3,3),
 "總統辯論季":(3,4,2,3),
 "十月驚奇窗口":(4,2,3,4),
 "財政年度開始":(3,5,3,3),
 "大選日":(5,5,5,5),
 "選後 FOMC（~）":(4,4,4,4),
 # ---- YEAR 5 ----
 "交接期：市場定價下任新政":(4,4,3,5),
 "新國會就任":(2,5,3,2),
 "卸任／下任就職（週期第1461日）":(3,5,4,4),
}
# generic FOMC / recurring-calendar fallbacks by keyword
def fallback(node,cat,why):
    if "點陣圖" in node:   return (4,4,4,3)   # SEP meetings bind the path
    if "FOMC" in node:     return (3,4,3,2)   # plain meetings
    if "主席證詞" in node:  return (3,5,3,3)
    if "Jackson Hole" in node: return (4,3,4,3)
    if "報稅日" in node:    return (3,5,2,3)
    if "財政年度開始" in node: return (4,5,3,3)
    if "預算案" in node:    return (3,4,4,3)
    if "債務上限" in node:  return (4,3,4,4)
    if "國情咨文" in node:  return (2,4,3,2)
    if "國會就任" in node:  return (2,5,3,2)
    if "收官" in node:      return (3,5,2,4)
    return (2,3,2,2)

# YEAR-position multiplier: the same calendar node does NOT carry the same weight
# in every cycle year — the 26-term evidence says Y2 nodes bind hardest.
YMULT={0:1.00, 1:0.96, 2:1.10, 3:1.00, 4:1.02, 5:0.94}

rows=[]
for i,x in enumerate(N,1):
    # look up per-cycle-year first, then by bare node name, then keyword fallback
    sub=S.get(f'{x["node"]}|Y{x["y"]}') or S.get(x["node"]) or fallback(x["node"],x["cat"],x["why"])
    M,I,P,E=sub
    raw=M*W["M"]+I*W["I"]+P*W["P"]+E*W["E"]          # 1..5
    # normalise against the true maximum (raw 5 x best year-multiplier) so nothing
    # is clipped at 100 and every node keeps a distinct, comparable position
    MAXP=5*max(YMULT.values())
    score=round((raw*YMULT[x["y"]]-1)/(MAXP-1)*100,1)
    if   score>=85: band="★★★★★ 決定級"
    elif score>=70: band="★★★★ 高"
    elif score>=50: band="★★★ 中"
    elif score>=30: band="★★ 低"
    else:           band="★ 背景"
    rows.append({**x,"idx":i,"M":M,"I":I,"P":P,"E":E,
                 "raw":round(raw,2),"ymult":YMULT[x["y"]],"score":score,"band":band})

json.dump(rows,open(os.path.join(ROOT,"data","nodes100_scored.json"),"w"),ensure_ascii=False,indent=1)

print(f"scored {len(rows)} nodes")
from collections import Counter
print("bands:",dict(Counter(r["band"] for r in rows)))
print("\nTop 15 by score:")
for r in sorted(rows,key=lambda z:-z["score"])[:15]:
    print(f"  {r['score']:5.1f} {r['band'][:6]:8s} Y{r['y']} {r['when']:18s} {r['node']}")
print("\nBottom 5:")
for r in sorted(rows,key=lambda z:z["score"])[:5]:
    print(f"  {r['score']:5.1f} Y{r['y']} {r['node']}")
import statistics as st
v=[r["score"] for r in rows]
print(f"\nscore range {min(v)}–{max(v)}  median {st.median(v)}  mean {round(st.mean(v),1)}")
