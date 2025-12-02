#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量将 PDF 转为纯文本
"""

from pathlib import Path
from pypdf import PdfReader

PAIRS = [
    ("1绪言.pdf", "1绪言.txt"),
    ("2进程管理.pdf", "2进程管理.txt"),
    ("3处理机调度.pdf", "3处理机调度.txt"),
    ("4存储管理.pdf", "4存储管理.txt"),
    ("7文件管理.pdf", "7文件管理.txt"),
    ("死锁.pdf", "死锁.txt"),
]


def convert(pdf_path: Path, txt_path: Path):
    reader = PdfReader(pdf_path)
    with txt_path.open("w", encoding="utf-8") as out:
        for idx, page in enumerate(reader.pages, 1):
            text = page.extract_text() or ""
            out.write(f"--- Page {idx} ---\n{text}\n\n")
    print(f"已生成 {txt_path}")


def main():
    root = Path(__file__).parent
    for pdf_name, txt_name in PAIRS:
        pdf_path = root / pdf_name
        txt_path = root / txt_name
        if not pdf_path.exists():
            print(f"跳过，文件不存在：{pdf_path}")
            continue
        convert(pdf_path, txt_path)


if __name__ == "__main__":
    main()


