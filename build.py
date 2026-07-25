#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Regenerate both deliverables (HTML + Excel) from committed data/ + assets/.

Usage:  python3 build.py
Requires:  pip install openpyxl pandas

Full pipeline (from the two source spreadsheets in source/) lives in pipeline/;
this top-level build regenerates the presentation layer from the derived JSON in data/.
Outputs: 美國總統任期_EasyHard資金市場週期_R1.html and .xlsx
"""
import subprocess, sys, os
ROOT = os.path.dirname(os.path.abspath(__file__))
for script in ("pipeline/8_gen_html.py", "pipeline/9_gen_excel.py",
               "pipeline/8b_gen_r2_html.py", "pipeline/9b_gen_r2_excel.py",
               "pipeline/6d_anchor.py", "pipeline/8c_gen_anchor_html.py"):
    print(f"→ running {script}")
    subprocess.run([sys.executable, os.path.join(ROOT, script)], check=True)
print("✓ R1 + R2百年版 + R2現任錨定版 regenerated")
