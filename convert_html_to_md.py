#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
将HTML习题文件转换为Markdown格式
只提取题目和正确答案
"""

import os
import re
from bs4 import BeautifulSoup
from pathlib import Path


def clean_text(text, preserve_newlines=False):
    """清理文本，去除多余的空白字符"""
    if not text:
        return ""
    # 去除HTML标签残留
    text = re.sub(r'<[^>]+>', '', text)
    
    if preserve_newlines:
        # 保留换行符，但清理多余的空白
        lines = text.split('\n')
        cleaned_lines = [line.strip() for line in lines if line.strip()]
        return '\n'.join(cleaned_lines)
    else:
        # 去除多余的空白字符
        text = ' '.join(text.split())
        return text.strip()


def extract_question_number_and_content(h3_tag):
    """从h3标签中提取题号和题目内容"""
    # 获取h3标签的文本
    full_text = h3_tag.get_text()
    
    # 查找题号（如 "1. "）
    match = re.match(r'(\d+)\.\s*', full_text)
    if match:
        question_num = match.group(1)
        # 提取题目内容（在题号和分数信息之后）
        # 查找题目内容部分
        qt_content = h3_tag.find('span', class_='qtContent')
        if qt_content:
            # 处理HTML内容，将<br/>转换为换行
            content_html = str(qt_content)
            # 将<br>和<br/>替换为换行符
            content_html = re.sub(r'<br\s*/?>', '\n', content_html, flags=re.IGNORECASE)
            # 创建临时soup来解析
            temp_soup = BeautifulSoup(content_html, 'html.parser')
            question_content = clean_text(temp_soup.get_text(), preserve_newlines=True)
        else:
            # 如果没有找到qtContent，尝试从文本中提取
            # 移除题号和分数信息
            question_content = re.sub(r'^\d+\.\s*\([^)]+\)\s*', '', full_text)
            question_content = clean_text(question_content, preserve_newlines=True)
        return question_num, question_content
    
    return None, None


def extract_options(ul_tag):
    """提取选项"""
    options = []
    if not ul_tag:
        return options
    
    li_tags = ul_tag.find_all('li', class_='workTextWrap')
    for li in li_tags:
        option_text = clean_text(li.get_text())
        if option_text:
            options.append(option_text)
    
    return options


def extract_answer(question_div):
    """提取正确答案"""
    # 先尝试查找span标签（单选题等）
    right_answer_span = question_div.find('span', class_='rightAnswerContent')
    if right_answer_span:
        # 处理HTML内容，将<br/>转换为换行
        answer_html = str(right_answer_span)
        answer_html = re.sub(r'<br\s*/?>', '\n', answer_html, flags=re.IGNORECASE)
        temp_soup = BeautifulSoup(answer_html, 'html.parser')
        answer = clean_text(temp_soup.get_text(), preserve_newlines=True)
        # 清理末尾的分号和多余空白
        answer = answer.rstrip(';').strip()
        return answer
    
    # 再尝试查找dd标签（简答题等）
    right_answer_dd = question_div.find('dd', class_='rightAnswerContent')
    if right_answer_dd:
        # 处理HTML内容，将<br/>转换为换行
        answer_html = str(right_answer_dd)
        answer_html = re.sub(r'<br\s*/?>', '\n', answer_html, flags=re.IGNORECASE)
        temp_soup = BeautifulSoup(answer_html, 'html.parser')
        answer = clean_text(temp_soup.get_text(), preserve_newlines=True)
        # 清理末尾的分号和多余空白
        answer = answer.rstrip(';').strip()
        return answer
    
    return ""


def convert_html_to_md(html_file_path, output_dir=None):
    """将HTML文件转换为Markdown格式"""
    # 读取HTML文件
    with open(html_file_path, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    # 解析HTML
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # 提取作业标题
    title_tag = soup.find('h2', class_='mark_title')
    title = title_tag.get_text().strip() if title_tag else Path(html_file_path).stem
    
    # 提取所有题目
    questions = []
    question_divs = soup.find_all('div', class_='questionLi')
    
    for question_div in question_divs:
        # 提取题号和题目内容
        h3_tag = question_div.find('h3', class_='mark_name')
        if not h3_tag:
            continue
        
        question_num, question_content = extract_question_number_and_content(h3_tag)
        if not question_num or not question_content:
            continue
        
        # 提取选项
        ul_tag = question_div.find('ul', class_='qtDetail')
        options = extract_options(ul_tag)
        
        # 提取正确答案
        answer = extract_answer(question_div)
        
        questions.append({
            'num': question_num,
            'content': question_content,
            'options': options,
            'answer': answer
        })
    
    # 生成Markdown内容
    md_content = f"# {title}\n\n"
    
    for q in questions:
        md_content += f"## {q['num']}. {q['content']}\n\n"
        
        # 添加选项
        if q['options']:
            for option in q['options']:
                md_content += f"{option}\n\n"
        
        # 添加正确答案
        if q['answer']:
            md_content += f"**正确答案：{q['answer']}**\n\n"
        
        md_content += "---\n\n"
    
    # 确定输出文件路径
    if output_dir is None:
        output_dir = os.path.dirname(html_file_path)
    
    output_file = os.path.join(output_dir, f"{Path(html_file_path).stem}.md")
    
    # 写入Markdown文件
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(md_content)
    
    print(f"已转换: {html_file_path} -> {output_file}")
    return output_file


def main():
    """主函数：批量转换所有HTML文件"""
    # 获取脚本所在目录的父目录（习题目录）
    script_dir = Path(__file__).parent
    exercise_dir = script_dir / "习题"
    
    if not exercise_dir.exists():
        print(f"错误：找不到习题目录 {exercise_dir}")
        return
    
    # 获取所有HTML文件
    html_files = list(exercise_dir.glob("*.html"))
    
    if not html_files:
        print("未找到HTML文件")
        return
    
    print(f"找到 {len(html_files)} 个HTML文件，开始转换...\n")
    
    # 转换每个HTML文件
    for html_file in html_files:
        try:
            convert_html_to_md(str(html_file))
        except Exception as e:
            print(f"转换 {html_file} 时出错: {e}")
    
    print(f"\n转换完成！共处理 {len(html_files)} 个文件")


if __name__ == "__main__":
    main()

