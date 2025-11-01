#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小红圈数据抓取系统主程序
"""

import os
import sys
import argparse
from red_ring_crawler import RedRingCrawler
from process_existing_content import process_existing_content


def setup_environment():
    """设置环境"""
    print("小红圈数据抓取系统")
    print("=" * 50)
    
    # 检查必要的依赖
    try:
        import requests
        import sqlite3
        print("✓ 基础依赖检查通过")
    except ImportError as e:
        print(f"✗ 缺少依赖: {e}")
        print("请安装必要的依赖: pip install requests")
        return False
    
    return True


def show_menu():
    """显示主菜单"""
    print("\n请选择操作:")
    print("1. 使用Playwright抓取数据 (需要安装Playwright)")
    print("2. 处理已获取的页面内容")
    print("3. 查看数据库统计信息")
    print("4. 查看最近的文章")
    print("5. 专门抓取精华帖子 (推荐)")
    print("6. 退出")
    
    choice = input("\n请输入选择 (1-6): ").strip()
    return choice


def option_playwright_crawl():
    """选项1: 使用Playwright抓取数据"""
    try:
        from playwright_crawler import PlaywrightRedRingCrawler
        import asyncio
        
        print("开始使用Playwright抓取数据...")
        crawler = PlaywrightRedRingCrawler()
        asyncio.run(crawler.crawl_and_save())
        
    except ImportError:
        print("Playwright未安装，请先安装: pip install playwright")
        print("安装后还需要安装浏览器: playwright install")
        return False
    
    return True


def option_essence_crawl():
    """选项6: 专门抓取精华帖子"""
    try:
        from essence_crawler import EssenceCrawler
        import asyncio
        
        print("开始专门抓取精华帖子...")
        crawler = EssenceCrawler()
        asyncio.run(crawler.crawl_essence_posts())
        
    except ImportError:
        print("Playwright未安装，请先安装: pip install playwright")
        print("安装后还需要安装浏览器: playwright install")
        return False
    
    return True


def option_process_existing_content():
    """选项2: 处理已获取的页面内容"""
    print("处理已获取的页面内容")
    print("请将页面内容粘贴到下方 (输入END结束):")
    
    content_lines = []
    while True:
        line = input()
        if line.strip() == "END":
            break
        content_lines.append(line)
    
    content = "\n".join(content_lines)
    
    if not content.strip():
        print("未输入任何内容")
        return False
    
    process_existing_content(content)
    return True


def option_show_stats():
    """选项3: 显示数据库统计信息"""
    crawler = RedRingCrawler()
    stats = crawler.get_database_stats()
    
    print("\n数据库统计信息:")
    print(f"总文章数: {stats['total_articles']}")
    print(f"精华文章数: {stats['essence_articles']}")
    print(f"总评论数: {stats['total_comments']}")
    print(f"总文件数: {stats['total_files']}")
    
    # 显示文章列表
    if stats['total_articles'] > 0:
        print("\n最近的文章:")
        import sqlite3
        conn = sqlite3.connect(crawler.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT title, author, publish_date, likes_count, is_essence 
            FROM articles 
            ORDER BY publish_date DESC 
            LIMIT 10
        ''')
        
        articles = cursor.fetchall()
        for i, article in enumerate(articles, 1):
            title, author, date, likes, is_essence = article
            essence_mark = " [精华]" if is_essence else ""
            print(f"{i}. {title}{essence_mark}")
            print(f"   作者: {author}, 日期: {date}, 点赞: {likes}")
        
        conn.close()
    
    return True


def option_show_recent_articles():
    """选项4: 显示最近的文章详情"""
    crawler = RedRingCrawler()
    stats = crawler.get_database_stats()
    
    if stats['total_articles'] == 0:
        print("数据库中暂无文章数据")
        return False
    
    import sqlite3
    conn = sqlite3.connect(crawler.db_path)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT title, author, publish_date, content, likes_count, comments_count, is_essence, is_pinned
        FROM articles 
        ORDER BY publish_date DESC 
        LIMIT 5
    ''')
    
    articles = cursor.fetchall()
    
    for i, article in enumerate(articles, 1):
        title, author, date, content, likes, comments, is_essence, is_pinned = article
        
        print(f"\n{'='*60}")
        print(f"文章 {i}: {title}")
        print(f"{'='*60}")
        
        marks = []
        if is_essence:
            marks.append("精华")
        if is_pinned:
            marks.append("置顶")
        
        if marks:
            print(f"标签: {', '.join(marks)}")
        
        print(f"作者: {author}")
        print(f"发布日期: {date}")
        print(f"点赞: {likes} | 评论: {comments}")
        print(f"\n内容预览:")
        print(content[:200] + "..." if len(content) > 200 else content)
        print()
    
    conn.close()
    return True


def main():
    """主函数"""
    if not setup_environment():
        return
    
    while True:
        choice = show_menu()
        
        if choice == '1':
            option_playwright_crawl()
        elif choice == '2':
            option_process_existing_content()
        elif choice == '3':
            option_show_stats()
        elif choice == '4':
            option_show_recent_articles()
        elif choice == '5':
            option_essence_crawl()
        elif choice == '6':
            print("感谢使用小红圈数据抓取系统！")
            break
        else:
            print("无效选择，请重新输入")
        
        input("\n按回车键继续...")


if __name__ == "__main__":
    # 命令行参数支持
    parser = argparse.ArgumentParser(description='小红圈数据抓取系统')
    parser.add_argument('--crawl', action='store_true', help='使用Playwright抓取数据')
    parser.add_argument('--stats', action='store_true', help='显示数据库统计信息')
    parser.add_argument('--content', type=str, help='处理指定的页面内容文件')
    parser.add_argument('--essence', action='store_true', help='专门抓取精华帖子')
    
    args = parser.parse_args()
    
    if args.crawl:
        option_playwright_crawl()
    elif args.stats:
        option_show_stats()
    elif args.content:
        if os.path.exists(args.content):
            with open(args.content, 'r', encoding='utf-8') as f:
                content = f.read()
            process_existing_content(content)
        else:
            print(f"文件不存在: {args.content}")
    elif args.essence:
        option_essence_crawl()
    else:
        main()
