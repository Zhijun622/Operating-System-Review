#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
将习题md文件按照分类整理成五个md文件
"""

import os
import re
from pathlib import Path
from collections import defaultdict


def read_md_file(file_path):
    """读取md文件内容，返回标题和所有题目"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    lines = content.split('\n')
    if not lines:
        return None, []
    
    # 提取标题（第一行的#标题）
    title = None
    if lines[0].startswith('# '):
        title = lines[0][2:].strip()
    
    # 提取所有题目（##开头的部分）
    questions = []
    current_question = []
    in_question = False
    
    for line in lines[1:]:  # 跳过标题行
        if line.startswith('## '):
            # 新题目开始
            if current_question and in_question:
                questions.append('\n'.join(current_question))
            current_question = [line]
            in_question = True
        elif line.strip() == '---':
            # 题目结束
            if current_question:
                questions.append('\n'.join(current_question))
            current_question = []
            in_question = False
        elif in_question:
            current_question.append(line)
    
    # 处理最后一个题目
    if current_question and in_question:
        questions.append('\n'.join(current_question))
    
    return title, questions


def classify_files():
    """分类文件"""
    categories = {
        '绪论': ['绪论2.md', '作业详情.md'],
        '进程管理': ['进程的概念.md', '作业进程描述与状态.md', '进程调度1.md', '作业记录型信号量机制.md'],
        '死锁': ['死锁预防.md'],
        '存储管理': ['分区存储管理.md', '分页存储管理.md', '作业分段、段页式存储管理.md'],
        '文件系统': ['文件系统.md']
    }
    return categories


def merge_questions(category_name, file_list, exercise_dir):
    """合并某个分类的所有题目"""
    all_questions = []
    question_counter = 1
    
    for filename in file_list:
        file_path = exercise_dir / filename
        if not file_path.exists():
            print(f"警告：文件不存在 {file_path}")
            continue
        
        title, questions = read_md_file(file_path)
        if not questions:
            continue
        
        # 添加来源信息（可选）
        # all_questions.append(f"\n<!-- 来源：{title} -->\n")
        
        # 重新编号题目
        for question in questions:
            # 替换题号
            question = re.sub(r'^## (\d+)\.', f'## {question_counter}.', question, flags=re.MULTILINE)
            all_questions.append(question)
            all_questions.append('\n---\n')
            question_counter += 1
    
    return all_questions


def main():
    """主函数"""
    script_dir = Path(__file__).parent
    exercise_dir = script_dir / "习题"
    output_dir = script_dir
    
    if not exercise_dir.exists():
        print(f"错误：找不到习题目录 {exercise_dir}")
        return
    
    categories = classify_files()
    
    print("开始分类整理习题...\n")
    
    for category_name, file_list in categories.items():
        print(f"处理分类：{category_name}")
        print(f"  包含文件：{', '.join(file_list)}")
        
        # 合并题目
        questions = merge_questions(category_name, file_list, exercise_dir)
        
        if not questions:
            print(f"  警告：{category_name} 分类没有找到题目\n")
            continue
        
        # 生成Markdown内容
        md_content = f"# {category_name}\n\n"
        md_content += ''.join(questions)
        
        # 写入文件
        output_file = output_dir / f"{category_name}.md"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(md_content)
        
        question_count = len([q for q in questions if q.startswith('## ')])
        print(f"  已生成：{output_file} (包含 {question_count} 道题目)\n")
    
    print("分类整理完成！")


if __name__ == "__main__":
    main()

