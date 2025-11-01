#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试评论抓取功能
"""

import asyncio
import sqlite3
import os
from enhanced_essence_crawler import EnhancedEssenceCrawler


async def test_comments_crawler():
    """测试评论抓取功能"""
    print("🧪 测试评论抓取功能")
    print("=" * 40)
    
    # 清理旧的数据库文件
    if os.path.exists("red_ring_essence.db"):
        os.remove("red_ring_essence.db")
    if os.path.exists("login_state.json"):
        os.remove("login_state.json")
    
    crawler = EnhancedEssenceCrawler()
    
    print("开始测试评论抓取功能...")
    print("注意: 系统将自动处理登录状态")
    print("⚠️  评论抓取可能需要较长时间，请耐心等待")
    
    # 测试抓取1页的精华帖子及评论
    success = await crawler.crawl_essence_posts_with_comments(max_pages=1)
    
    if success:
        print("\n✅ 评论抓取测试成功！")
        
        # 验证数据库内容
        conn = sqlite3.connect("red_ring_essence.db")
        cursor = conn.cursor()
        
        # 获取帖子统计
        cursor.execute('SELECT COUNT(*) FROM essence_posts')
        total_posts = cursor.fetchone()[0]
        
        # 获取评论统计
        cursor.execute('SELECT COUNT(*) FROM post_comments')
        total_comments = cursor.fetchone()[0]
        
        # 获取抓取记录
        cursor.execute('SELECT crawl_date, pages_crawled, posts_count, comments_count FROM crawl_logs ORDER BY id DESC LIMIT 1')
        latest_crawl = cursor.fetchone()
        
        conn.close()
        
        print(f"\n📊 测试结果统计:")
        print(f"精华帖子数: {total_posts}")
        print(f"评论数: {total_comments}")
        
        if latest_crawl:
            date, pages, posts, comments = latest_crawl
            print(f"抓取记录: {date} (抓取 {pages} 页, {posts} 个帖子, {comments} 条评论)")
        
        # 显示数据库文件信息
        db_size = os.path.getsize("red_ring_essence.db") if os.path.exists("red_ring_essence.db") else 0
        print(f"数据库文件大小: {db_size / 1024:.2f} KB")
        
        print("\n🎉 评论抓取功能测试完成！")
        
    else:
        print("\n❌ 评论抓取测试失败")


if __name__ == "__main__":
    asyncio.run(test_comments_crawler())
