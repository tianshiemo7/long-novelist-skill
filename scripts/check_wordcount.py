#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
章节字数检查脚本（适配 TXT 格式）
检查指定章节文件的中文字数
"""

import os
import re
import sys
from pathlib import Path

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')


def count_chinese_words(text: str) -> int:
    """统计中文字数（仅统计汉字，排除标点、数字、英文）"""
    chinese_chars = re.findall(r'[一-鿿]', text)
    return len(chinese_chars)


def count_total_chars(text: str) -> int:
    """统计总字符数（含标点，用于粗略统计）"""
    # 移除空白字符
    text = re.sub(r'\s+', '', text)
    return len(text)


def check_chapter(file_path: str, min_words: int = 3000) -> dict:
    """检查单个章节的字数"""
    path = Path(file_path)

    if not path.exists():
        return {
            'file': str(path),
            'exists': False,
            'chinese_word_count': 0,
            'total_chars': 0,
            'status': 'error',
            'message': f'文件不存在: {file_path}'
        }

    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()

    chinese_count = count_chinese_words(content)
    total_count = count_total_chars(content)

    status = 'pass' if chinese_count >= min_words else 'fail'
    message = f'中文字数: {chinese_count:,}' + (
        f' (✓ 达标)' if chinese_count >= min_words else f' (✗ 不足，需要至少 {min_words:,} 字)'
    )

    return {
        'file': str(path),
        'exists': True,
        'chinese_word_count': chinese_count,
        'total_chars': total_count,
        'status': status,
        'message': message
    }


def check_all_chapters(directory: str, pattern: str = '第*.txt', min_words: int = 3000) -> list:
    """检查目录下所有章节文件"""
    dir_path = Path(directory)
    if not dir_path.exists():
        print(f'错误: 目录不存在 - {directory}')
        return []

    chapter_files = sorted(dir_path.glob(pattern))
    results = []

    for chapter_file in chapter_files:
        result = check_chapter(str(chapter_file), min_words)
        results.append(result)

    return results


def print_results(results: list, min_words: int = 3000):
    """打印检查结果"""
    if not results:
        print('没有找到章节文件')
        return

    total_chinese = 0
    total_all = 0
    passed = 0
    failed = 0

    print('\n' + '=' * 60)
    print('章节字数检查报告')
    print('=' * 60)

    for result in results:
        if not result['exists']:
            print(f'\n❌ {result["file"]}')
            print(f'   {result["message"]}')
            continue

        total_chinese += result['chinese_word_count']
        total_all += result['total_chars']
        if result['status'] == 'pass':
            passed += 1
            icon = '✅'
        else:
            failed += 1
            icon = '⚠️ '

        filename = Path(result["file"]).name
        pct = (result['chinese_word_count'] / min_words * 100) if min_words > 0 else 0
        bar = '█' * int(pct / 10) + '░' * (10 - int(pct / 10))
        print(f'\n{icon} {filename}')
        print(f'   [{bar}] {result["chinese_word_count"]:,} / {min_words:,} ({pct:.0f}%)')
        print(f'   总字符数: {result["total_chars"]:,}')
        if result['status'] == 'fail':
            gap = min_words - result['chinese_word_count']
            print(f'   ⚠ 还差 {gap:,} 字')

    print('\n' + '-' * 60)
    print(f'总计: {len(results)} 章 | {passed} 章达标 | {failed} 章不足')
    print(f'中文总字数: {total_chinese:,} | 总字符数: {total_all:,}')
    print('-' * 60)

    if failed > 0:
        print(f'\n⚠️  有 {failed} 章内容不足 {min_words:,} 字，建议使用扩充技巧')
        print(f'   参考: references/guides/content-expansion.md')


def main():
    """主函数"""
    min_words = 3000

    if len(sys.argv) < 2:
        print('用法:')
        print('  检查单个章节: python check_wordcount.py <章节TXT文件路径> [最小字数]')
        print('  检查所有章节: python check_wordcount.py --all <chapters目录> [最小字数]')
        print('')
        print('示例:')
        print('  python check_wordcount.py novels/故事/chapters/第01章-开端.txt')
        print('  python check_wordcount.py novels/故事/chapters/第01章-开端.txt 4000')
        print('  python check_wordcount.py --all novels/故事/chapters')
        print('  python check_wordcount.py --all novels/故事/chapters 5000')
        return

    if sys.argv[1] == '--all':
        if len(sys.argv) < 3:
            print('错误: 使用 --all 时需要指定目录路径')
            return
        directory = sys.argv[2]
        min_words = int(sys.argv[3]) if len(sys.argv) > 3 else 3000
        results = check_all_chapters(directory, min_words=min_words)
        print_results(results, min_words)
    else:
        file_path = sys.argv[1]
        min_words = int(sys.argv[2]) if len(sys.argv) > 2 else 3000
        result = check_chapter(file_path, min_words)
        print_results([result], min_words)


if __name__ == '__main__':
    main()
