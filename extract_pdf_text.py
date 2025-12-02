#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
将 PDF 转为纯文本
"""

from pathlib import Path
from pypdf import PdfReader

pdf_path = Path("计算机操作系统（慕课版） (汤小丹, 王红玲, 姜华, 汤子瀛) (Z-Library).pdf")
output_path = Path("cos_mooc.txt")

reader = PdfReader(pdf_path)
with output_path.open("w", encoding="utf-8") as out:
    for i, page in enumerate(reader.pages, 1):
        text = page.extract_text() or ""
        out.write(f"--- Page {i} ---\n{text}\n\n")

print(f"已生成 {output_path.resolve()}")