# -*- coding: utf-8 -*-
"""Excel deliverable: the 100 recurring presidency-cycle nodes, scored."""
import os, json, datetime as dt
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from openpyxl.chart import BarChart, Reference
from openpyxl.formatting.rule import DataBarRule

ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
R=json.load(open(os.path.join(ROOT,"data","nodes100_scored.json")))
HK=dt.datetime.now(dt.timezone(dt.timedelta(hours=8)))
OUT=os.path.join(ROOT,f"美國總統週期100節點_評分表 ({HK:%m-%d}_hk{HK:%H.%M}).xlsx")

HEAD=PatternFill("solid",fgColor="1F3A5F"); TITLE=PatternFill("solid",fgColor="12263F")
SUB=PatternFill("solid",fgColor="E9EEF5")
W=Font(color="FFFFFF",bold=True,size=11); TF=Font(color="FFFFFF",bold=True,size=13)
BOLD=Font(bold=True); MUT=Font(color="6B7890",size=10)
thin=Side(style="thin",color="C9D2DF"); BORD=Border(left=thin,right=thin,top=thin,bottom=thin)
CEN=Alignment(horizontal="center",vertical="center",wrap_text=True)
LEFT=Alignment(horizontal="left",vertical="center",wrap_text=True)
LT=Alignment(horizontal="left",vertical="top",wrap_text=True)
BAND={"★★★★★ 決定級":"F4B9C2","★★★★ 高":"F8D9A8","★★★ 中":"FFF0B3",
      "★★ 低":"DCE6F1","★ 背景":"EDEFF2"}
CAT={"Fed·流動性":"D6E4F7","選舉政治":"F7DCD6","財政·國會":"E2E0F5","市場週期":"D9F0E3"}
YLAB={0:"YEAR 0 當選→就職",1:"YEAR 1 就職年 2025",2:"YEAR 2 中期選舉年 2026",
      3:"YEAR 3 大選前年 2027",4:"YEAR 4 大選年 2028",5:"YEAR 5 交接"}

wb=openpyxl.Workbook(); wb.remove(wb.active)
def title(ws,t,span,row=1):
    ws.merge_cells(start_row=row,start_column=1,end_row=row,end_column=span)
    c=ws.cell(row,1,t); c.fill=TITLE; c.font=TF; c.alignment=LEFT
    ws.row_dimensions[row].height=26
def hdr(ws,row,labels,widths):
    for i,l in enumerate(labels,1):
        c=ws.cell(row,i,l); c.fill=HEAD; c.font=W; c.alignment=CEN; c.border=BORD
    for i,w in enumerate(widths,1): ws.column_dimensions[get_column_letter(i)].width=w
    ws.row_dimensions[row].height=30

# ================= 0. 評分方法 =================
ws=wb.create_sheet("0.評分方法")
title(ws,"總統週期 100 節點 — 重要性評分模型（可稽核、可重算）",6)
notes=[("評分是什麼","為每個節點打一個 0–100 的重要性分數，衡量它對 Easy/Hard 資金環境的影響力。"),
 ("四個維度","M 市場衝擊力（權重40%）｜I 不可迴避性（20%）｜P 政策不可逆性（20%）｜E 實證支持度（20%）。每維 1–5 分。"),
 ("M 市場衝擊力","該節點歷史上直接改變 E/H 判區的能力。5＝多次單獨造成制度級轉區（如中期選舉、9月/12月 FOMC）。"),
 ("I 不可迴避性","是否憲法/法定日曆、無法延期或取消。5＝憲法明定（大選日、就職日、報稅日、財政年度開始）。"),
 ("P 政策不可逆性","當日決定是否鎖死後續數月路徑。5＝點陣圖/首份預算/主席換屆這類「一錘定音」節點。"),
 ("E 實證支持度","本 repo 26 屆數據對其重要性的支持強度。5＝有明確統計（如 15/26 屆大底落於 Y2）。"),
 ("週期年係數","同一日曆節點在不同週期年份量不同。Y2＝1.10（26屆實證最吃重）、Y4＝1.02、Y0/Y3＝1.00、Y1＝0.96、Y5＝0.94。"),
 ("計算式","raw = M×0.4 + I×0.2 + P×0.2 + E×0.2（1–5）→ score = (raw × 年係數 − 1) ÷ (5×1.10 − 1) × 100。不封頂、不裁剪。"),
 ("分級","★★★★★ 決定級 ≥85｜★★★★ 高 ≥70｜★★★ 中 ≥50｜★★ 低 ≥30｜★ 背景 <30"),
 ("結果分佈",f"分數範圍 {min(r['score'] for r in R)}–{max(r['score'] for r in R)}；中位 56.6；決定級 6 個、高 13 個、中 48 個、低 25 個、背景 8 個。"),
 ("最高分節點","中期選舉日（Y2）100.0＝唯一滿分：M/I/P/E 四維皆 5，且落在權重最高的第2年。"),
 ("如何質疑","四個維度分開列出（D–G 欄），可只挑戰其中一維而不動其餘；改動 pipeline/6h_nodes100_score.py 的子分即可全表重算。"),
 ("節點入選門檻","只收結構性、屆屆重複的節點（憲法/Fed/財政日曆＋經26屆實證的週期季節窗），不收一次性事件。"),
 ("工作表","0.評分方法｜1.100節點總表(依週期順序)｜2.依分數排名｜3.分年統計(含圖)｜4.分類統計"),
 ("免責","評分為框架研究用的相對權重，非投資建議。2027–2028 的 FOMC 以慣常月份標示（~，日程未公佈）。")]
r=3
for k,v in notes:
    c=ws.cell(r,1,k); c.font=BOLD; c.fill=SUB; c.alignment=LT; c.border=BORD
    ws.merge_cells(start_row=r,start_column=2,end_row=r,end_column=6)
    c2=ws.cell(r,2,v); c2.alignment=LT; c2.border=BORD
    ws.row_dimensions[r].height=32; r+=1
ws.column_dimensions['A'].width=18
for col in "BCDEF": ws.column_dimensions[col].width=25

# ================= 1. 總表 =================
ws=wb.create_sheet("1.100節點總表")
title(ws,"每任總統都要面對、屆屆重臨的 100 個重大時間節點（依週期順序）",11)
hdr(ws,3,["#","週期年","時點（現任錨定）","節點","類別","M\n市場衝擊","I\n不可迴避","P\n政策不可逆","E\n實證支持","分數","分級與 E/H 意義"],
    [5,17,17,30,12,8,8,8,8,8,52])
r=4
for x in R:
    vals=[x["idx"],YLAB[x["y"]],x["when"],x["node"],x["cat"],x["M"],x["I"],x["P"],x["E"],x["score"],
          f'{x["band"]}　{x["why"]}']
    for j,v in enumerate(vals,1):
        c=ws.cell(r,j,v); c.border=BORD
        c.alignment=LT if j==11 else (LEFT if j in(3,4) else CEN)
        if j==4: c.font=BOLD
        if j==5 and CAT.get(x["cat"]): c.fill=PatternFill("solid",fgColor=CAT[x["cat"]])
        if j==10:
            c.font=Font(bold=True,size=12)
            c.fill=PatternFill("solid",fgColor=BAND[x["band"]])
        if j==11: c.fill=PatternFill("solid",fgColor=BAND[x["band"]])
    r+=1
last=r-1
ws.conditional_formatting.add(f"J4:J{last}",
    DataBarRule(start_type="num",start_value=0,end_type="num",end_value=100,color="5B9BD5"))
ws.freeze_panes="A4"
ws.auto_filter.ref=f"A3:K{last}"

# ================= 2. 依分數排名 =================
ws=wb.create_sheet("2.依分數排名")
title(ws,"100 節點依重要性分數排名（高→低）",8)
hdr(ws,3,["名次","分數","分級","週期年","時點","節點","類別","E/H 意義"],
    [6,8,15,17,17,30,12,60])
r=4
for i,x in enumerate(sorted(R,key=lambda z:(-z["score"],z["idx"])),1):
    vals=[i,x["score"],x["band"],YLAB[x["y"]],x["when"],x["node"],x["cat"],x["why"]]
    for j,v in enumerate(vals,1):
        c=ws.cell(r,j,v); c.border=BORD
        c.alignment=LT if j==8 else (LEFT if j in(5,6) else CEN)
        if j==6: c.font=BOLD
        if j in(2,3): c.fill=PatternFill("solid",fgColor=BAND[x["band"]])
        if j==2: c.font=Font(bold=True,size=12)
        if j==7 and CAT.get(x["cat"]): c.fill=PatternFill("solid",fgColor=CAT[x["cat"]])
    r+=1
ws.conditional_formatting.add(f"B4:B{r-1}",
    DataBarRule(start_type="num",start_value=0,end_type="num",end_value=100,color="ED7D31"))
ws.freeze_panes="A4"; ws.auto_filter.ref=f"A3:H{r-1}"

# ================= 3. 分年統計 =================
ws=wb.create_sheet("3.分年統計")
title(ws,"各週期年的節點密度與平均重要性",7)
hdr(ws,3,["週期年","節點數","平均分","最高分","最高分節點","決定級(≥85)","高(70-85)"],
    [22,9,9,9,32,12,12])
r=4
import statistics as st
for y in range(6):
    g=[x for x in R if x["y"]==y]
    top=max(g,key=lambda z:z["score"])
    vals=[YLAB[y],len(g),round(st.mean([x["score"] for x in g]),1),top["score"],top["node"],
          sum(1 for x in g if x["score"]>=85),sum(1 for x in g if 70<=x["score"]<85)]
    for j,v in enumerate(vals,1):
        c=ws.cell(r,j,v); c.border=BORD; c.alignment=LEFT if j in(1,5) else CEN
        if j==1: c.font=BOLD
        if j==3: c.font=Font(bold=True); c.fill=PatternFill("solid",fgColor="FFF0B3")
    r+=1
ch=BarChart(); ch.type="col"; ch.title="各週期年平均重要性分數"
ch.y_axis.title="平均分"; ch.x_axis.title="週期年"; ch.height=9; ch.width=20
ch.add_data(Reference(ws,min_col=3,min_row=3,max_row=r-1),titles_from_data=True)
ch.set_categories(Reference(ws,min_col=1,min_row=4,max_row=r-1))
ch.series[0].graphicalProperties.solidFill="5B9BD5"
ws.add_chart(ch,"A12")
ch2=BarChart(); ch2.type="col"; ch2.title="各週期年節點數"
ch2.y_axis.title="節點數"; ch2.height=9; ch2.width=20
ch2.add_data(Reference(ws,min_col=2,min_row=3,max_row=r-1),titles_from_data=True)
ch2.set_categories(Reference(ws,min_col=1,min_row=4,max_row=r-1))
ch2.series[0].graphicalProperties.solidFill="70AD47"
ws.add_chart(ch2,"A31")

# ================= 4. 分類統計 =================
ws=wb.create_sheet("4.分類統計")
title(ws,"各類別的節點數與平均重要性",6)
hdr(ws,3,["類別","節點數","平均分","最高分","最高分節點","說明"],[15,9,9,9,30,50])
DESC={"Fed·流動性":"近半節點屬此類——流動性環是決定 E/H 的最強單一槓桿",
      "選舉政治":"決定政策時序：苦藥在 Y1-Y2、糖在 Y3",
      "財政·國會":"停擺/債務上限/預算＝結構性風險日",
      "市場週期":"由 26 屆實證推導的季節窗，非日曆事件"}
r=4
for cat in ["Fed·流動性","選舉政治","財政·國會","市場週期"]:
    g=[x for x in R if x["cat"]==cat]
    top=max(g,key=lambda z:z["score"])
    vals=[cat,len(g),round(st.mean([x["score"] for x in g]),1),top["score"],top["node"],DESC[cat]]
    for j,v in enumerate(vals,1):
        c=ws.cell(r,j,v); c.border=BORD; c.alignment=LT if j==6 else (LEFT if j in(1,5) else CEN)
        if j==1: c.font=BOLD; c.fill=PatternFill("solid",fgColor=CAT[cat])
        if j==3: c.font=Font(bold=True)
    r+=1
ch3=BarChart(); ch3.type="bar"; ch3.title="各類別平均重要性分數"
ch3.height=8; ch3.width=18
ch3.add_data(Reference(ws,min_col=3,min_row=3,max_row=r-1),titles_from_data=True)
ch3.set_categories(Reference(ws,min_col=1,min_row=4,max_row=r-1))
ch3.series[0].graphicalProperties.solidFill="ED7D31"
ws.add_chart(ch3,"A10")

wb.save(OUT)
print("written:",os.path.basename(OUT))
print("sheets:",wb.sheetnames)
