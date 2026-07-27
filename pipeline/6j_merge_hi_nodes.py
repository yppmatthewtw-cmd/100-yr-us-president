# -*- coding: utf-8 -*-
"""R9 — merge the 45 score>60 nodes into the anchor dataset for the PANE 1 layer."""
import os, json
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
A=json.load(open(os.path.join(ROOT,"data","anchor_r5.json")))
HI=json.load(open(os.path.join(ROOT,"data","hi_nodes.json")))
A["hi_nodes"]=HI
json.dump(A, open(os.path.join(ROOT,"data","anchor_r9.json"),"w"), separators=(',',':'), ensure_ascii=False)
print(f"anchor_r9.json written — {len(HI)} high-importance nodes merged")
