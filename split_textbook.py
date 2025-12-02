#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
将 cos_mooc.txt 按照复习大纲拆分成五个 Markdown 文件：
绪论、进程管理、死锁、存储管理、文件系统
"""

from pathlib import Path
import re

ROOT = Path(__file__).parent
SOURCE_TXT = ROOT / "cos_mooc.txt"

OUTPUT_MAP = {
    "绪论": ["1"],
    "进程管理": ["2", "3a", "4"],
    "死锁": ["3b"],
    "存储管理": ["5", "6"],
    "文件系统": ["7", "8", "9"],
}


def load_lines():
    if not SOURCE_TXT.exists():
        raise FileNotFoundError(f"找不到源文件 {SOURCE_TXT}")
    text = SOURCE_TXT.read_text(encoding="utf-8", errors="ignore")
    return text.splitlines()


def find_chapter_ranges(lines):
    """返回 {章节号: (start_idx, end_idx)}"""
    chapter_markers = []
    pattern = re.compile(r"^第(\d+)章$")
    for idx, line in enumerate(lines):
        match = pattern.match(line.strip())
        if match:
            chapter_markers.append((int(match.group(1)), idx))

    chapter_markers.sort(key=lambda x: x[1])
    ranges = {}
    for i, (chap, start) in enumerate(chapter_markers):
        end = chapter_markers[i + 1][1] if i + 1 < len(chapter_markers) else len(lines)
        ranges[chap] = (start, end)
    return ranges


def split_chapter3(lines, chapter_ranges):
    """返回 (前半部分索引范围, 后半部分索引范围)"""
    if 3 not in chapter_ranges:
        raise ValueError("未找到第3章内容")
    start, end = chapter_ranges[3]
    pattern = re.compile(r"^3\.5")
    deadlock_start = None
    for idx in range(start, end):
        if pattern.match(lines[idx].strip()):
            deadlock_start = idx
            break
    if deadlock_start is None:
        raise ValueError("未在第3章中找到 3.5 死锁部分")

    proc_part = (start, deadlock_start)
    deadlock_part = (deadlock_start, end)
    return proc_part, deadlock_part


def collect_segments(lines, ranges, chapter3_parts):
    proc_part, deadlock_part = chapter3_parts
    segments = {
        "1": [ranges[1]],
        "2": [ranges[2]],
        "3a": [proc_part],
        "3b": [deadlock_part],
        "4": [ranges[4]],
        "5": [ranges[5]],
        "6": [ranges[6]],
        "7": [ranges.get(7, (0, 0))],
        "8": [ranges.get(8, (0, 0))],
        "9": [ranges.get(9, (0, 0))],
    }
    return segments


def write_category_files(lines, segments):
    for category, keys in OUTPUT_MAP.items():
        collected = []
        for key in keys:
            for seg in segments.get(key, []):
                start, end = seg
                if start >= end:
                    continue
                collected.extend(lines[start:end])
                if not collected or collected[-1] != "":
                    collected.append("")
        if not collected:
            print(f"警告：{category} 未收集到内容，跳过")
            continue
        output_path = ROOT / f"{category}-教材.md"
        header = [f"# {category}", ""]
        output_lines = header + collected
        output_path.write_text("\n".join(output_lines), encoding="utf-8")
        print(f"已生成 {output_path}")


def main():
    lines = load_lines()
    ranges = find_chapter_ranges(lines)
    required_chapters = [1, 2, 3, 4, 5, 6, 7, 8, 9]
    missing = [chap for chap in required_chapters if chap not in ranges]
    if missing:
        raise ValueError(f"缺少章节：{missing}")
    chapter3_parts = split_chapter3(lines, ranges)
    segments = collect_segments(lines, ranges, chapter3_parts)
    write_category_files(lines, segments)


if __name__ == "__main__":
    main()


