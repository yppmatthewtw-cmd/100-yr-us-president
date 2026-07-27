# -*- coding: utf-8 -*-
"""R2 — build the 100-year (26-term) Excel workbook."""
import os, json
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from openpyxl.chart import LineChart, Reference

ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
S=os.path.join(ROOT,"data")
OUT=os.path.join(ROOT,"美國總統任期_EasyHard資金市場週期_R2.xlsx")
C=json.load(open(f"{S}/century.json")); pkg=json.load(open(f"{S}/package.json"))
M,ORDER,MAT,PS,YS=C["meta"],C["order"],C["matrix"],C["phase_summary"],C["yearstats"]
TR,MT=C["troughs"],C["midterm"]

GREEN=PatternFill("solid",fgColor="CDEBDB"); AMBER=PatternFill("solid",fgColor="F8E7BE"); RED=PatternFill("solid",fgColor="F6CBD0")
GREEN_D=PatternFill("solid",fgColor="7FCFA8"); AMBER_D=PatternFill("solid",fgColor="EFC96F"); RED_D=PatternFill("solid",fgColor="EE9AA6")
HEADF=PatternFill("solid",fgColor="1F3A5F"); TITLEF=PatternFill("solid",fgColor="12263F"); SUBF=PatternFill("solid",fgColor="E9EEF5")
WHITE=Font(color="FFFFFF",bold=True,size=11); TITLEFONT=Font(color="FFFFFF",bold=True,size=13)
BOLD=Font(bold=True); MUT=Font(color="6B7890",size=10)
thin=Side(style="thin",color="C9D2DF"); BORD=Border(left=thin,right=thin,top=thin,bottom=thin)
CEN=Alignment(horizontal="center",vertical="center",wrap_text=True)
LEFT=Alignment(horizontal="left",vertical="center",wrap_text=True)
LEFTT=Alignment(horizontal="left",vertical="top",wrap_text=True)
def zf(v,deep=False):
    if v is None: return None
    if v>=70: return GREEN_D if deep else GREEN
    if v<=40: return RED_D if deep else RED
    return AMBER_D if deep else AMBER
def zn(v): return "EASY" if v>=70 else ("HARD" if v<=40 else "UNC")

wb=openpyxl.Workbook(); wb.remove(wb.active)
def title(ws,text,span,row=1):
    ws.merge_cells(start_row=row,start_column=1,end_row=row,end_column=span)
    c=ws.cell(row,1,text); c.fill=TITLEF; c.font=TITLEFONT; c.alignment=LEFT
    ws.row_dimensions[row].height=26
def hdr(ws,row,labels,widths=None):
    for i,l in enumerate(labels,1):
        c=ws.cell(row,i,l); c.fill=HEADF; c.font=WHITE; c.alignment=CEN; c.border=BORD
    if widths:
        for i,w in enumerate(widths,1): ws.column_dimensions[get_column_letter(i)].width=w

# ---------- 0 說明 ----------
ws=wb.create_sheet("0.說明與方法")
title(ws,"美國總統任期 × Easy/Hard 資金市場週期 R2 — 百年 26 屆（1925–2029）統一週期比較",6)
nA=sum(1 for n in ORDER if M[n]["tier"]=="A"); nB=sum(1 for n in ORDER if M[n]["tier"]=="B")
notes=[("R2 是什麼","把 1925–2029 全部 26 屆美國總統任期，疊在同一條『就任週期軸』上比較資金鬆緊。X＝總統週期日（就職＝第0日），Y＝Easy/Hard 指數(0–100)。"),
 ("★ 資料分兩層","本表最重要的前提：26 屆並非同一種資料來源，兩層分開標示、絕不混用。"),
 (f"TIER A 量測級（{nA} 屆）","2016-07→2026-07。直接採用 A-(Fable) 檔案的每日 18 指標加權合成分，逐日判區。涵蓋 特朗普I／拜登／特朗普II（奧巴馬II 為混合）。"),
 (f"TIER B 重建級（{nB} 屆）","1925→2016-07。無每日指標數據，依 R1 自身列明的逐屆 EASY/HARD 窗口，對照有紀錄市場史（見頂見底日、Fed 轉向、危機）轉寫為分段階梯指數。屬分段級，非偽造的每日序列。"),
 ("Tier B 評分表","；".join(f"{v}={k}" for k,v in sorted(C['rubric'].items(),key=lambda kv:-kv[1]))),
 ("判區門檻","指數 ≥70 = EASY／40–70 = UNCERTAIN／≤40 = HARD（與 R1 同一套門檻）"),
 ("週期對齊","以就職日為第 0 日，按週抽樣；交接期（週期日<0）取前一任的區段值（任期連續，故此段本就屬前任）。"),
 ("見底位置","不由指數推導（階梯序列的最低值會落在區段起點，是方法假象），改採逐屆有紀錄的實際收市見底日。"),
 ("主要發現①",f"15/26 屆（58%）的任內大底落在第2年（中期選舉年），與 R1 表列的 15 次樣本完全一致；第3年僅 1 屆。"),
 ("主要發現②",f"第3年平均指數 {YS['第3年 大選前年']['avg']:.1f}、中位 {YS['第3年 大選前年']['med']:.1f}，為四年最高，26 屆中僅 {YS['第3年 大選前年']['hard_terms']} 屆落入 HARD。"),
 ("主要發現③",f"見底月份應更新為 Q4 而非 8–10 月：15 次中期年大底中 Q4 佔 {MT['q4']}/15、12 月佔 {MT['dec']}/15（1974、1994、2018、2022）。"),
 ("主要發現④","『同期處 HARD 的屆數%』在週期第 409 日（約 1.12 年，即第2年開頭）達到高峰 38%，是百年尺度上風險最集中的位置。"),
 ("工作表","0.說明 | 1.週期熱圖數據 | 2.週期階段矩陣 | 3.見底位置 | 4.週期年統計 | 5.逐屆分段全表 | 6.週期原型曲線(含圖) | 7.百年R1原表"),
 ("免責","市場史/框架研究，非投資建議。Tier B 為依公開紀錄的重建，判讀時請留意層級標示。"),
]
r=3
for k,v in notes:
    ws.cell(r,1,k).font=BOLD; ws.cell(r,1).fill=SUBF; ws.cell(r,1).alignment=LEFTT; ws.cell(r,1).border=BORD
    ws.merge_cells(start_row=r,start_column=2,end_row=r,end_column=6)
    c=ws.cell(r,2,v); c.alignment=LEFTT; c.border=BORD
    ws.row_dimensions[r].height=32; r+=1
ws.column_dimensions['A'].width=22
for col in 'BCDEF': ws.column_dimensions[col].width=26

# ---------- 1 週期熱圖數據 ----------
ws=wb.create_sheet("1.週期熱圖數據")
title(ws,"週期熱圖數據 — 26 屆 × 總統週期日的 Easy/Hard 指數（顏色＝所屬區）",4+len(ORDER))
hdr(ws,3,["週期日","週期年","約年"]+[M[n]["cn"] for n in ORDER],
    widths=[9,12,8]+[11]*len(ORDER))
idx={n:{p["cd"]:p for p in C["series"][n]} for n in ORDER}
cds=sorted({p["cd"] for n in ORDER for p in C["series"][n]})
r=4
for cd in cds:
    yl="交接期" if cd<0 else f"第{min(4,cd//365+1)}年"
    ws.cell(r,1,cd).alignment=CEN; ws.cell(r,2,yl).alignment=CEN
    ws.cell(r,3,round(cd/365.25,2)).alignment=CEN
    for j,n in enumerate(ORDER,4):
        p=idx[n].get(cd)
        c=ws.cell(r,j, p["v"] if p else None); c.alignment=CEN
        if p and zf(p["v"]): c.fill=zf(p["v"])
    r+=1
ws.freeze_panes="D4"

# ---------- 2 週期階段矩陣 ----------
ws=wb.create_sheet("2.週期階段矩陣")
ph=C["phases"]
title(ws,"週期階段矩陣 — 26 屆 × 8 個週期階段的平均 Easy/Hard 指數",3+len(ph))
hdr(ws,3,["總統（任期）","年代","層"]+[p["key"] for p in ph], widths=[20,10,7]+[15]*len(ph))
r=4
for n in ORDER:
    m=M[n]
    ws.cell(r,1,f"{m['cn']} {m['inaug'][:4]}–{m['end'][:4]}").font=BOLD
    ws.cell(r,1).border=BORD; ws.cell(r,1).alignment=LEFT
    ws.cell(r,2,m["era"]).alignment=CEN; ws.cell(r,2).border=BORD
    ws.cell(r,3,m["tier"]).alignment=CEN; ws.cell(r,3).border=BORD; ws.cell(r,3).font=BOLD
    for j,p in enumerate(ph,4):
        v=MAT[n].get(p["key"])
        c=ws.cell(r,j, f"{v['avg']:.1f} (H{v['hard']}%)" if v else "—")
        c.alignment=CEN; c.border=BORD
        if v and zf(v["avg"]): c.fill=zf(v["avg"]); c.font=BOLD
    r+=1
ws.cell(r,1,"26 屆彙總").font=Font(bold=True,size=11); ws.cell(r,1).border=BORD
ws.cell(r,2,"—").alignment=CEN; ws.cell(r,3,"—").alignment=CEN
for j,p in enumerate(ph,4):
    s=PS[p["key"]]
    c=ws.cell(r,j, f"平均{s['avg']:.1f} 中位{s['med']:.1f}\n{s['terms_hard']}/{s['terms']}屆HARD")
    c.alignment=CEN; c.border=BORD; c.font=BOLD
    if zf(s["avg"]): c.fill=zf(s["avg"],deep=True)
ws.freeze_panes="D4"

# ---------- 3 見底位置 ----------
ws=wb.create_sheet("3.見底位置")
title(ws,"見底位置 — R1「大級別底部落在第2年（中期選舉年）」的百年驗證",6)
hdr(ws,3,["總統（任期）","實際見底日","週期日","落在週期年","是否 R1 的15次樣本","依據／說明"],
    widths=[20,14,10,13,17,42])
r=4
for n in ORDER:
    t=TR.get(n)
    if not t: continue
    m=M[n]
    vals=[f"{m['cn']} {m['inaug'][:4]}–{m['end'][:4]}",t["date"],t["cd"],t["year"],
          "★ 是" if t["midterm_low"] else "",t["note"]]
    for j,v in enumerate(vals,1):
        c=ws.cell(r,j,v); c.border=BORD; c.alignment=LEFTT if j==6 else CEN
        if j==1: c.font=BOLD; c.alignment=LEFT
        if j==4 and v=="第2年": c.fill=RED_D; c.font=BOLD
        if j==5 and v: c.fill=AMBER_D; c.font=BOLD
    r+=1
r+=1
yd=C["trough_year_dist"]; tot=sum(yd.values())
ws.cell(r,1,"落在各週期年的屆數").font=Font(bold=True,size=12); r+=1
hdr(ws,r,["週期年","屆數","佔比"],widths=None)
r+=1
for k in ["第1年","第2年","第3年","第4年"]:
    v=yd.get(k,0)
    ws.cell(r,1,k).border=BORD; ws.cell(r,1).alignment=CEN
    ws.cell(r,2,v).border=BORD; ws.cell(r,2).alignment=CEN
    ws.cell(r,3,f"{v/tot*100:.0f}%").border=BORD; ws.cell(r,3).alignment=CEN
    if k=="第2年":
        for j in (1,2,3): ws.cell(r,j).fill=RED_D; ws.cell(r,j).font=BOLD
    r+=1
r+=1
ws.merge_cells(start_row=r,start_column=1,end_row=r+2,end_column=6)
c=ws.cell(r,1,f"月份分佈修正：R1 的 15 次中期年大底中，8–10月 {MT['aug_oct']}/15、Q4(10–12月) {MT['q4']}/15、"
              f"其中 12 月 {MT['dec']}/15（1974、1994、2018、2022）。R1 原述『集中 8–10 月』方向正確，"
              f"但更準確的說法是『集中於 Q4』；現代樣本普遍更晚，因為見底時點由 Fed 轉向時點決定。")
c.alignment=LEFTT; c.border=BORD

# ---------- 4 週期年統計 ----------
ws=wb.create_sheet("4.週期年統計")
title(ws,"總統週期年統計（26 屆）— Easy/Hard 指數 vs R1 報酬原型",8)
hdr(ws,3,["週期年","平均指數","中位","HARD 屆數","EASY 屆數","最差一屆","最佳一屆","R1 原型"],
    widths=[18,11,9,12,12,20,20,26])
arche={"第1年 就職年":"~+7% 蜜月＋開刀","第2年 中期選舉年":"~+5% 最弱／-17% 回撤",
       "第3年 大選前年":"~+16.8% 最強","第4年 大選年":"~+7% 前高後震"}
r=4
for k,y in YS.items():
    vals=[k,round(y["avg"],1),round(y["med"],1),f"{y['hard_terms']}/{y['terms']}",f"{y['easy_terms']}/{y['terms']}",
          f"{M[y['worst']]['cn']} ({y['worst_v']:.0f})",f"{M[y['best']]['cn']} ({y['best_v']:.0f})",arche.get(k,"")]
    for j,v in enumerate(vals,1):
        c=ws.cell(r,j,v); c.border=BORD; c.alignment=LEFTT if j==8 else CEN
        if j==1: c.font=BOLD; c.alignment=LEFT
        if j==2 and zf(y["avg"]): c.fill=zf(y["avg"],deep=True); c.font=BOLD
    r+=1

# ---------- 5 逐屆分段全表 ----------
ws=wb.create_sheet("5.逐屆分段全表")
title(ws,"逐屆 Easy/Hard 分段全表（Tier B 重建明細，可逐條與 R1 原表稽核）",5)
hdr(ws,3,["總統（任期）","期間","指數","級別","依據／事件"],widths=[20,26,8,10,60])
r=4
for n in ORDER:
    m=M[n]
    if not m["segs"]:
        ws.cell(r,1,f"{m['cn']} {m['inaug'][:4]}–{m['end'][:4]}").font=BOLD
        ws.cell(r,1).border=BORD; ws.cell(r,1).alignment=LEFT
        ws.merge_cells(start_row=r,start_column=2,end_row=r,end_column=5)
        c=ws.cell(r,2,"Tier A 量測級 — 直接採用每日 18 指標加權合成分，不使用重建分段（見 R1 報告逐日分段）")
        c.border=BORD; c.alignment=LEFT; c.font=MUT; c.fill=GREEN
        r+=1; continue
    for i,s in enumerate(m["segs"]):
        ws.cell(r,1, f"{m['cn']} {m['inaug'][:4]}–{m['end'][:4]}" if i==0 else "").font=BOLD
        ws.cell(r,1).border=BORD; ws.cell(r,1).alignment=LEFT
        vals=[f"{s['s']} → {s['e']}",s["v"],s["lv"],s["note"]]
        for j,v in enumerate(vals,2):
            c=ws.cell(r,j,v); c.border=BORD; c.alignment=LEFTT if j==5 else CEN
            if j==3 and zf(s["v"]): c.fill=zf(s["v"]); c.font=BOLD
        r+=1
ws.freeze_panes="A4"

# ---------- 6 週期原型曲線 (+chart) ----------
ws=wb.create_sheet("6.週期原型曲線")
title(ws,"週期原型曲線 — 26 屆中位數 / 四分位 / 同期處 HARD 的屆數%",6)
hdr(ws,3,["週期日","約年","26屆中位數","P25","P75","同期處HARD屆數%"],widths=[10,8,14,10,10,17])
r=4
for e in C["envelope"]:
    for j,v in enumerate([e["cd"],round(e["cd"]/365.25,2),e["med"],e["p25"],e["p75"],e["hardpct"]],1):
        c=ws.cell(r,j,v); c.alignment=CEN
    if zf(e["med"]): ws.cell(r,3).fill=zf(e["med"])
    r+=1
last=r-1
ch=LineChart(); ch.title="26 屆總統週期原型：Easy/Hard 指數中位數與四分位帶"
ch.style=2; ch.height=11; ch.width=30
ch.y_axis.title="Easy/Hard 指數"; ch.x_axis.title="總統週期日（就職日 = 0）"
ch.y_axis.scaling.min=0; ch.y_axis.scaling.max=100
ch.add_data(Reference(ws,min_col=3,max_col=5,min_row=3,max_row=last),titles_from_data=True)
ch.set_categories(Reference(ws,min_col=1,min_row=4,max_row=last))
for i,col in enumerate(["FFB020","9FB3CC","9FB3CC"]):
    s=ch.series[i]; s.smooth=False; s.graphicalProperties.line.solidFill=col
    s.graphicalProperties.line.width=28000 if i==0 else 12000
ws.add_chart(ch,f"H4")
ch2=LineChart(); ch2.title="同一週期位置上，26 屆中處於 HARD 的比例"
ch2.style=2; ch2.height=9; ch2.width=30
ch2.y_axis.title="處 HARD 的屆數 %"; ch2.x_axis.title="總統週期日（就職日 = 0）"
ch2.add_data(Reference(ws,min_col=6,min_row=3,max_row=last),titles_from_data=True)
ch2.set_categories(Reference(ws,min_col=1,min_row=4,max_row=last))
ch2.series[0].graphicalProperties.line.solidFill="D2566C"; ch2.series[0].graphicalProperties.line.width=24000
ch2.series[0].smooth=False
ws.add_chart(ch2,"H27")
ws.freeze_panes="B4"

# ---------- 7 百年R1原表 ----------
ws=wb.create_sheet("7.百年R1原表")
title(ws,"百年逐屆 Easy/Hard（R1 原表）— Tier B 分段的主要依據",4)
hdr(ws,3,["總統（任期）","EASY Money 窗口","HARD Money 窗口","關鍵數據與事件"],widths=[18,40,40,40])
r=4
for h in pkg["hist"]:
    for j,v in enumerate([h["pres"],h.get("easy"),h.get("hard"),h.get("events")],1):
        c=ws.cell(r,j,v); c.border=BORD; c.alignment=LEFTT
        if j==1: c.font=BOLD
    r+=1

wb.save(OUT)
print("R2 Excel written:",os.path.basename(OUT))
print("sheets:",wb.sheetnames)
