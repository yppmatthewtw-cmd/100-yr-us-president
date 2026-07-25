import os
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# -*- coding: utf-8 -*-
"""Build the presidency EASY/HARD Excel workbook from computed + enriched data."""
import json, datetime
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

S=os.path.join(ROOT,"data")
OUT=os.path.join(ROOT,"presidency_easyhard.xlsx")
pkg=json.load(open(f"{S}/package.json"))
seg=pkg['segments']; cy=pkg['cycleyears']
keydates=json.load(open(f"{S}/keydates.json"))
enriched=json.load(open(f"{S}/enriched.json"))
daily=json.load(open(f"{S}/daily.json"))
ENR={p['name']:p for p in enriched['presidents']}
SYN=enriched['synthesis']
ORDER=["Obama II","Trump I","Biden","Trump II"]
PARTY={"Obama II":"民主黨","Trump I":"共和黨","Biden":"民主黨","Trump II":"共和黨"}
TERM={"Obama II":"2013–2017","Trump I":"2017–2021","Biden":"2021–2025","Trump II":"2025–2029"}

# styles
C_HEAD="1F3A5F"; C_SUB="2E4A73"; C_TITLE="12263F"
GREEN=PatternFill("solid",fgColor="CDEBDB"); AMBER=PatternFill("solid",fgColor="F8E7BE"); RED=PatternFill("solid",fgColor="F6CBD0")
HEADF=PatternFill("solid",fgColor=C_HEAD); SUBF=PatternFill("solid",fgColor="E9EEF5"); TITLEF=PatternFill("solid",fgColor=C_TITLE)
WHITE=Font(color="FFFFFF",bold=True,size=11); TITLEFONT=Font(color="FFFFFF",bold=True,size=13)
BOLD=Font(bold=True); MUT=Font(color="6B7890",size=10)
thin=Side(style="thin",color="C9D2DF"); BORD=Border(left=thin,right=thin,top=thin,bottom=thin)
CEN=Alignment(horizontal="center",vertical="center",wrap_text=True)
LEFT=Alignment(horizontal="left",vertical="center",wrap_text=True)
LEFTT=Alignment(horizontal="left",vertical="top",wrap_text=True)
def zfill(z):
    z=(z or "")[0:1]
    return GREEN if z=="E" else (AMBER if z=="U" else (RED if z=="H" else None))
def zname(z):
    return {"E":"EASY 寬鬆","U":"UNCERTAIN 震盪","H":"HARD 緊縮","EASY":"EASY 寬鬆","UNCERTAIN":"UNCERTAIN 震盪","HARD":"HARD 緊縮"}.get(z,z or "")

wb=openpyxl.Workbook(); wb.remove(wb.active)

def hdr(ws,row,labels,widths=None,fill=HEADF,font=WHITE):
    for i,l in enumerate(labels,1):
        c=ws.cell(row,i,l); c.fill=fill; c.font=font; c.alignment=CEN; c.border=BORD
    if widths:
        for i,w in enumerate(widths,1): ws.column_dimensions[get_column_letter(i)].width=w
def title(ws,text,span,row=1):
    ws.merge_cells(start_row=row,start_column=1,end_row=row,end_column=span)
    c=ws.cell(row,1,text); c.fill=TITLEF; c.font=TITLEFONT; c.alignment=LEFT
    ws.row_dimensions[row].height=26

# ============ Sheet 0: 說明 ============
ws=wb.create_sheet("0.說明與方法")
title(ws,"美國總統任期 × Easy/Hard 資金市場週期 — 以 NDX 十年每日三區實證重定義",6)
notes=[
 ("資料來源①","A-(Fable) EasyHardMoney 三區指標庫及 NDX 十年每日分段 2026R4.5.3_2 — 每日判區(02A)、18指標合成分、Fed政策步階(07)"),
 ("資料來源②","美國總統任期百年 EasyHard 資金市場週期 R1 — 百年逐屆定性框架與總統週期統計"),
 ("判區引擎","18項量化指標(技術/趨勢、廣度、流動性/政策、信用、波動率、情緒)加權合成分: ≥70=EASY / 40–70=UNCERTAIN / ≤40=HARD"),
 ("數據載體","NDX(納指100)每日收盤, 2016-07-08 → 2026-07-10, 共 2,515 個交易日"),
 ("全期分佈","EASY 1,757日(69.9%) / UNCERTAIN 441日(17.5%) / HARD 317日(12.6%)"),
 ("分段方法","以 02A 每日 ZONE 為實證輸入, 平滑成最短10交易日的制度級分段(去除純分數版單日跳動雜訊), 得各任總統精確的 Easy/Hard 起訖日與 NDX 點位"),
 ("總統週期年","以就職年為第1年, 按日曆年切分(第2年=中期選舉年, 第4年=大選年); 對照 R1 百年原型"),
 ("五個經濟環","① 政治/總統週期 ② 流動性/Fed環 ③ 信用環(HY利差) ④ 實體經濟/景氣環 ⑤ 黑天鵝/地緣環"),
 ("覆蓋任期","Obama II(僅任期尾2016.7起)、Trump I(全)、Biden(全)、Trump II(進行中至2026.7); 其餘26屆保留R1定性框架"),
 ("重大事件","經多代理AI對照公開歷史紀錄查核(Fed決議、QE/QT、戰爭、關稅、危機), 見各任事件表"),
 ("免責","市場史/框架研究, 非投資建議。平均值因統計口徑略有出入, 形態結論穩健。"),
 ("工作表","0.說明 | 1.橫向週期比較 | 2.逐任實證分段 | 3.週期年度統計 | 4.重大事件 | 5.經濟五環對應 | 6.關鍵節點 | 7.百年R1全表 | 8.Fed政策步階 | 9.NDX每日數據"),
]
r=3
for k,v in notes:
    ws.cell(r,1,k).font=BOLD; ws.cell(r,1).fill=SUBF; ws.cell(r,1).alignment=LEFTT; ws.cell(r,1).border=BORD
    ws.merge_cells(start_row=r,start_column=2,end_row=r,end_column=6)
    c=ws.cell(r,2,v); c.alignment=LEFTT; c.border=BORD
    ws.row_dimensions[r].height=30; r+=1
ws.column_dimensions['A'].width=16
for col in 'BCDEF': ws.column_dimensions[col].width=26
ws.freeze_panes="A3"

# ============ Sheet 1: 橫向週期比較 ============
ws=wb.create_sheet("1.橫向週期比較")
title(ws,"橫向總統週期比較(2016–2026 四任實證) — 資金區 × NDX表現 × 主因",8)
hdr(ws,3,["總統","第1年 就職","第2年 中期選舉","第3年 大選前","第4年 大選","符合度","點題"],
    widths=[12,26,26,26,26,10,30])
r=4
for c in SYN.get('comparison',[]):
    vals=[c.get('president'),c.get('y1'),c.get('y2'),c.get('y3'),c.get('y4'),c.get('conforms'),c.get('note')]
    for i,v in enumerate(vals,1):
        cell=ws.cell(r,i,v); cell.border=BORD; cell.alignment=LEFTT if i in(2,3,4,5,7) else CEN
        if i==1: cell.font=BOLD
    r+=1
r+=1
ws.cell(r,1,"偏離百年原型的例外").font=Font(bold=True,size=12); r+=1
hdr(ws,r,["例外任期","成因分類與說明"],widths=None); ws.column_dimensions['B'].width=26
er=r+1
for x in SYN.get('exceptions',[]):
    ws.cell(er,1,x.get('name')).border=BORD; ws.cell(er,1).font=BOLD; ws.cell(er,1).alignment=LEFTT
    ws.merge_cells(start_row=er,start_column=2,end_row=er,end_column=7)
    cc=ws.cell(er,2,x.get('desc')); cc.border=BORD; cc.alignment=LEFTT; er+=1
er+=1
if SYN.get('summary'):
    ws.cell(er,1,"橫向總結").font=Font(bold=True,size=12); er+=1
    ws.merge_cells(start_row=er,start_column=1,end_row=er+3,end_column=7)
    cc=ws.cell(er,1,SYN['summary']); cc.alignment=LEFTT; cc.border=BORD; er+=4
if SYN.get('now_2026'):
    ws.cell(er,1,"現在定位 2026").font=Font(bold=True,size=12); er+=1
    ws.merge_cells(start_row=er,start_column=1,end_row=er+3,end_column=7)
    cc=ws.cell(er,1,SYN['now_2026']); cc.alignment=LEFTT; cc.border=BORD
ws.freeze_panes="A4"

# ============ Sheet 2: 逐任實證分段 ============
ws=wb.create_sheet("2.逐任實證分段")
title(ws,"逐任總統 — NDX 每日三區實證分段(平滑後制度級, 最短10交易日)",8)
hdr(ws,3,["總統","資金區","起","訖","交易日","NDX起→訖","期內漲跌%","備註"],
    widths=[12,15,12,12,9,18,11,30])
r=4
# recompute intra-segment lo/hi/return from daily for notes
dd={datetime.date.fromisoformat(x['date']):x['ndx'] for x in daily}
dlist=sorted(dd.items())
for name in ORDER:
    for i,g in enumerate(seg.get(name,[])):
        z=g['zone']
        chg=(g['ndx_end']/g['ndx_start']-1)*100
        # intra low/high
        s0=datetime.date.fromisoformat(g['start']); s1=datetime.date.fromisoformat(g['end'])
        within=[(k,v) for k,v in dlist if s0<=k<=s1]
        note=""
        if within:
            lo=min(within,key=lambda t:t[1]); hi=max(within,key=lambda t:t[1])
            if z=="HARD": note=f"段內低 {lo[1]:.0f}@{lo[0].isoformat()}"
            elif z=="EASY": note=f"段內高 {hi[1]:.0f}@{hi[0].isoformat()}"
            else: note=f"低{lo[1]:.0f} 高{hi[1]:.0f}"
        vals=[name if i==0 else "",zname(z),g['start'],g['end'],g['days'],
              f"{g['ndx_start']:.0f}→{g['ndx_end']:.0f}",f"{chg:+.1f}%",note]
        for j,v in enumerate(vals,1):
            cell=ws.cell(r,j,v); cell.border=BORD
            cell.alignment=CEN if j in(2,3,4,5,6,7) else LEFT
            if j==1: cell.font=BOLD
            if j==2 and zfill(z): cell.fill=zfill(z); cell.font=BOLD
        r+=1
    # spacer
    for j in range(1,9): ws.cell(r,j).fill=PatternFill("solid",fgColor="F2F5F9")
    r+=1
ws.freeze_panes="A4"

# ============ Sheet 3: 週期年度統計 ============
ws=wb.create_sheet("3.週期年度統計")
title(ws,"總統週期年度統計(實證) vs 百年原型 — 資金區% · NDX年內回報 · 最大回撤",9)
hdr(ws,3,["總統","週期年","日曆年","EASY%","UNC%","HARD%","NDX年內%","最大回撤%","峰→谷 / 原型對照"],
    widths=[12,16,9,9,9,9,11,11,34])
arch={1:"~+7% 蜜月+開刀",2:"~+5% 最弱/-17%回撤/中期見底",3:"~+16.8% 最強",4:"~+7% 前高後震"}
r=4
for name in ORDER:
    yrs=cy.get(name,{}).get('years',{})
    for k in ["1","2","3","4"]:
        y=yrs.get(k)
        if not y: continue
        dom="E" if y['easy']>=max(y['unc'],y['hard']) else ("H" if y['hard']>=y['unc'] else "U")
        pt=f"{y['peak']}→{y['trough']}" if y['maxdd']<-3 else "—"
        note=f"{pt} | 原型:{arch[int(k)]}"
        vals=[name if k=="1" or (name=="Obama II") else "",y['label'],y['cal'],
              f"{y['easy']*100:.0f}%",f"{y['unc']*100:.0f}%",f"{y['hard']*100:.0f}%",
              f"{y['ret']:+.1f}%",f"{y['maxdd']:.0f}%",note]
        for j,v in enumerate(vals,1):
            cell=ws.cell(r,j,v); cell.border=BORD; cell.alignment=CEN if j!=9 else LEFTT
            if j==1: cell.font=BOLD
        # color the dominant-zone row lightly
        ws.cell(r,4).fill=GREEN; ws.cell(r,5).fill=AMBER; ws.cell(r,6).fill=RED
        r+=1
    for j in range(1,10): ws.cell(r,j).fill=PatternFill("solid",fgColor="F2F5F9")
    r+=1
ws.freeze_panes="A4"

# ============ Sheet 4: 重大事件 ============
ws=wb.create_sheet("4.重大事件時間軸")
title(ws,"重大事件時間軸 — Fed利率 · 貨幣政策/QE · 戰爭/地緣 · 財政/關稅 · 危機/黑天鵝",6)
hdr(ws,3,["總統","日期","類別","事件","說明","對NDX/市場影響"],widths=[11,12,13,30,44,26])
r=4
for name in ORDER:
    evs=sorted(ENR.get(name,{}).get('events',[]),key=lambda e:e.get('date',''))
    for i,e in enumerate(evs):
        vals=[name if i==0 else "",e.get('date'),e.get('category'),e.get('title'),e.get('detail'),e.get('ndx_effect')]
        for j,v in enumerate(vals,1):
            cell=ws.cell(r,j,v); cell.border=BORD; cell.alignment=CEN if j in(2,3) else LEFTT
            if j==1: cell.font=BOLD
            if j==4: cell.font=BOLD
        r+=1
    for j in range(1,7): ws.cell(r,j).fill=PatternFill("solid",fgColor="F2F5F9")
    r+=1
ws.freeze_panes="A4"

# ============ Sheet 5: 經濟五環 ============
ws=wb.create_sheet("5.經濟五環對應")
title(ws,"各實證分段 × 經濟五環對應 — 政治/流動性/信用/景氣/黑天鵝",8)
hdr(ws,3,["總統","實證分段","區","驅動力","①政治環","②流動性/Fed環","③信用環","④景氣環 / ⑤黑天鵝環"],
    widths=[11,22,10,26,24,24,22,30])
r=4
for name in ORDER:
    zds=ENR.get(name,{}).get('zone_drivers',[])
    for i,d in enumerate(zds):
        z=d.get('zone') or (d.get('segment','').split()[0] if d.get('segment') else '')
        ring45=f"景氣: {d.get('ring_business','')}\n黑天鵝: {d.get('ring_blackswan','')}"
        vals=[name if i==0 else "",d.get('segment'),zname(z),d.get('driver'),
              d.get('ring_political'),d.get('ring_liquidity'),d.get('ring_credit'),ring45]
        for j,v in enumerate(vals,1):
            cell=ws.cell(r,j,v); cell.border=BORD; cell.alignment=LEFTT
            if j==1: cell.font=BOLD
            if j==3 and zfill(z): cell.fill=zfill(z); cell.font=BOLD
        r+=1
    for j in range(1,9): ws.cell(r,j).fill=PatternFill("solid",fgColor="F2F5F9")
    r+=1
ws.freeze_panes="A4"

# ============ Sheet 6: 關鍵節點 ============
ws=wb.create_sheet("6.關鍵節點")
title(ws,"關鍵節點定位 — 就職 · 首100日 · 中期選舉 · 大選(當時所處資金區)",5)
hdr(ws,3,["總統","日期","關鍵節點","當時資金區","NDX"],widths=[13,13,22,16,12])
r=4
for name in ORDER:
    for i,e in enumerate(keydates.get(name,[])):
        z=e.get('zone'); ndx=f"{e['ndx']:.0f}" if e.get('ndx') else "—"
        vals=[name if i==0 else "",e['date'],e['label'],zname(z) if z else "數據外",ndx]
        for j,v in enumerate(vals,1):
            cell=ws.cell(r,j,v); cell.border=BORD; cell.alignment=CEN if j!=3 else LEFT
            if j==1: cell.font=BOLD
            if j==4 and zfill(z): cell.fill=zfill(z); cell.font=BOLD
        r+=1
    for j in range(1,6): ws.cell(r,j).fill=PatternFill("solid",fgColor="F2F5F9")
    r+=1
ws.freeze_panes="A4"

# ============ Sheet 7: 百年R1全表 ============
ws=wb.create_sheet("7.百年R1全表")
title(ws,"百年逐屆 Easy/Hard(1925–2026, R1全表) — ★=本報告NDX實證重定義",4)
hdr(ws,3,["總統(任期)","EASY Money 窗口","HARD Money 窗口","關鍵數據與事件"],widths=[18,40,40,40])
r=4
cov=("Obama II","Trump I","Biden","Trump II")
for h in pkg['hist']:
    star="★ " if any(h['pres'].startswith(k) for k in cov) else ""
    vals=[star+h['pres'],h.get('easy'),h.get('hard'),h.get('events')]
    for j,v in enumerate(vals,1):
        cell=ws.cell(r,j,v); cell.border=BORD; cell.alignment=LEFTT
        if j==1: cell.font=BOLD
    if star:
        for j in range(1,5): ws.cell(r,j).fill=PatternFill("solid",fgColor="E4EDFA")
    r+=1
ws.freeze_panes="A4"

# ============ Sheet 8: Fed政策步階 ============
ws=wb.create_sheet("8.Fed政策步階")
title(ws,"Fed L1 政策方向步階(公開紀錄重建) — 流動性環骨架",4)
hdr(ws,3,["生效日","方向碼","方向","Fed 政策狀態"],widths=[14,9,10,60])
r=4
for p in pkg['l1policy']:
    dirn={1:"寬鬆",0:"中性",-1:"緊縮"}.get(p['code'],"")
    fill={1:GREEN,0:None,-1:RED}.get(p['code'])
    vals=[p['date'],p['code'],dirn,p['state']]
    for j,v in enumerate(vals,1):
        cell=ws.cell(r,j,v); cell.border=BORD; cell.alignment=CEN if j in(1,2,3) else LEFTT
        if j==3 and fill: cell.fill=fill; cell.font=BOLD
    r+=1
ws.freeze_panes="A4"

# ============ Sheet 9: NDX每日數據 ============
ws=wb.create_sheet("9.NDX每日數據")
title(ws,"NDX 每日判區數據(實證輸入, 2016-07 → 2026-07)",5)
hdr(ws,3,["日期","總統","NDX收盤","合成分","資金區"],widths=[13,12,12,10,15])
PRES_RANGES=[("Obama II","2013-01-20","2017-01-20"),("Trump I","2017-01-20","2021-01-20"),
             ("Biden","2021-01-20","2025-01-20"),("Trump II","2025-01-20","2029-01-20")]
def whichp(ds):
    d=datetime.date.fromisoformat(ds)
    for n,s,e in PRES_RANGES:
        if datetime.date.fromisoformat(s)<=d<datetime.date.fromisoformat(e): return n
    return ""
r=4
for x in daily:
    vals=[x['date'],whichp(x['date']),round(x['ndx'],1),x['score'],zname(x['zone'])]
    for j,v in enumerate(vals,1):
        cell=ws.cell(r,j,v); cell.border=Border(bottom=Side(style="hair",color="E5E9F0"))
        cell.alignment=CEN if j!=2 else LEFT
        if j==5 and zfill(x['zone']): cell.fill=zfill(x['zone'])
    r+=1
ws.freeze_panes="A4"

wb.save(OUT)
print("Excel written:",OUT)
print("sheets:",wb.sheetnames)
