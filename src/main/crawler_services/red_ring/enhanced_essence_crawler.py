#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
增强版小红圈精华帖子爬虫 - 支持登录状态保持和分页抓取
"""

import asyncio
import sqlite3
import time
import random
import json
import os
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class EnhancedEssenceCrawler:
    def __init__(self, db_path: str = "red_ring_essence.db"):
        """
        初始化增强版精华帖子爬虫
        
        Args:
            db_path: SQLite数据库文件路径
        """
        self.db_path = db_path
        self.base_url = "https://www.red-ring.cn/group/14775"
        self.essence_url = f"{self.base_url}?tab=essence"
        self.login_state_file = "login_state.json"
        
        # 初始化数据库
        self._init_database()
    
    def _init_database(self):
        """初始化SQLite数据库表结构"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 创建精华帖子表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS essence_posts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                content TEXT,
                author TEXT,
                publish_date TEXT,
                likes_count INTEGER DEFAULT 0,
                comments_count INTEGER DEFAULT 0,
                view_count INTEGER DEFAULT 0,
                is_pinned BOOLEAN DEFAULT FALSE,
                tags TEXT,
                summary TEXT,
                page_number INTEGER DEFAULT 1,
                post_url TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 创建评论回复表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS post_comments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                post_id INTEGER,
                comment_author TEXT,
                comment_content TEXT,
                comment_date TEXT,
                is_author_reply BOOLEAN DEFAULT FALSE,
                reply_to_comment_id INTEGER,
                likes_count INTEGER DEFAULT 0,
                comment_type TEXT DEFAULT 'comment',  -- comment, reply
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (post_id) REFERENCES essence_posts (id)
            )
        ''')
        
        # 创建抓取记录表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS crawl_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                crawl_date TEXT,
                pages_crawled INTEGER,
                posts_count INTEGER,
                comments_count INTEGER DEFAULT 0,
                success BOOLEAN,
                error_message TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 创建登录状态表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS login_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_data TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
        logger.info(f"增强版精华帖子数据库初始化完成: {self.db_path}")
    
    async def ensure_login(self, page):
        """
        确保用户已登录，如果未登录则提示用户扫码登录
        
        Args:
            page: Playwright页面对象
            
        Returns:
            是否已登录
        """
        # 检查是否已登录
        is_logged_in = await self._check_login_status(page)
        
        if is_logged_in:
            logger.info("用户已登录")
            return True
        
        # 如果未登录，提示用户扫码登录
        logger.info("检测到未登录状态，请扫码登录...")
        print("\n🔐 请扫码登录小红圈账号")
        print("   系统将打开浏览器窗口，请使用微信扫码登录")
        print("   登录成功后，系统会自动继续抓取数据")
        print("   " + "-" * 40)
        
        # 导航到登录页面
        await page.goto("https://www.red-ring.cn/login", wait_until='networkidle')
        
        # 等待用户扫码登录
        login_success = await self._wait_for_login(page)
        
        if login_success:
            logger.info("用户登录成功")
            # 保存登录状态
            await self._save_login_state(page)
            return True
        else:
            logger.warning("用户登录超时或失败")
            return False
    
    async def _check_login_status(self, page) -> bool:
        """检查用户是否已登录"""
        try:
            # 检查是否有登录相关的元素
            login_elements = await page.query_selector_all('.login-btn, .login-button, [href*="login"]')
            user_elements = await page.query_selector_all('.user-avatar, .user-info, .user-name')
            
            # 如果有用户信息元素且没有登录按钮，则认为已登录
            if len(user_elements) > 0 and len(login_elements) == 0:
                return True
            
            # 检查页面标题或内容中是否包含登录相关信息
            page_content = await page.content()
            if "登录" in page_content and "注册" in page_content:
                return False
            
            return True
            
        except Exception as e:
            logger.warning(f"检查登录状态失败: {e}")
            return False
    
    async def _wait_for_login(self, page, timeout: int = 120) -> bool:
        """等待用户扫码登录"""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            # 检查是否登录成功
            is_logged_in = await self._check_login_status(page)
            
            if is_logged_in:
                return True
            
            # 等待一段时间再检查
            await asyncio.sleep(5)
            print("⏳ 等待登录中... (请使用微信扫码)")
        
        return False
    
    async def _save_login_state(self, page):
        """保存登录状态"""
        try:
            # 获取cookies
            cookies = await page.context.cookies()
            
            # 保存到文件
            state_data = {
                'cookies': cookies,
                'saved_at': datetime.now().isoformat()
            }
            
            with open(self.login_state_file, 'w', encoding='utf-8') as f:
                json.dump(state_data, f, ensure_ascii=False, indent=2)
            
            logger.info("登录状态已保存")
            
        except Exception as e:
            logger.warning(f"保存登录状态失败: {e}")
    
    async def _load_login_state(self, context):
        """加载登录状态"""
        try:
            if not os.path.exists(self.login_state_file):
                return False
            
            with open(self.login_state_file, 'r', encoding='utf-8') as f:
                state_data = json.load(f)
            
            # 检查状态是否过期（24小时）
            saved_at = datetime.fromisoformat(state_data['saved_at'])
            if (datetime.now() - saved_at).total_seconds() > 24 * 3600:
                logger.info("登录状态已过期")
                return False
            
            # 设置cookies
            await context.add_cookies(state_data['cookies'])
            logger.info("登录状态已加载")
            return True
            
        except Exception as e:
            logger.warning(f"加载登录状态失败: {e}")
            return False
    
    async def crawl_essence_posts_with_comments(self, max_pages: int = 10):
        """
        使用分页抓取精华帖子及其评论回复
        
        Args:
            max_pages: 最大抓取页数
            
        Returns:
            抓取是否成功
        """
        try:
            from playwright.async_api import async_playwright
            
            logger.info(f"开始分页抓取精华帖子及评论，最多 {max_pages} 页")
            
            async with async_playwright() as p:
                # 启动浏览器
                browser = await p.chromium.launch(
                    headless=False,
                    args=[
                        '--disable-blink-features=AutomationControlled',
                        '--disable-features=VizDisplayCompositor',
                        '--disable-background-timer-throttling',
                        '--disable-backgrounding-occluded-windows',
                        '--disable-renderer-backgrounding'
                    ]
                )
                
                # 创建上下文
                context = await browser.new_context(
                    viewport={'width': 1280, 'height': 720},
                    user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    extra_http_headers={
                        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
                        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
                        'Accept-Encoding': 'gzip, deflate, br',
                    }
                )
                
                # 尝试加载登录状态
                await self._load_login_state(context)
                
                page = await context.new_page()
                
                # 导航到精华页面
                logger.info(f"导航到精华页面: {self.essence_url}")
                await page.goto(self.essence_url, wait_until='networkidle')
                
                # 确保登录
                if not await self.ensure_login(page):
                    logger.error("登录失败，无法继续抓取")
                    await browser.close()
                    return False
                
                # 分页抓取
                all_posts = []
                total_comments = 0
                current_page = 1
                
                while current_page <= max_pages:
                    logger.info(f"开始抓取第 {current_page} 页")
                    
                    try:
                        # 等待页面稳定
                        await page.wait_for_load_state('networkidle')
                        await page.wait_for_timeout(2000)
                        
                        # 滚动页面加载更多内容
                        await self._scroll_page(page)
                        
                        # 获取页面内容
                        content = await self._get_page_content(page)
                        
                        if not content:
                            logger.warning(f"第 {current_page} 页未能获取到内容")
                            break
                        
                        # 解析精华帖子
                        page_posts = self._parse_essence_posts(content)
                        logger.info(f"第 {current_page} 页解析出 {len(page_posts)} 个精华帖子")
                        
                        # 标记页码
                        for post in page_posts:
                            post['page_number'] = current_page
                        
                        # 抓取每个帖子的评论和回复
                        for post in page_posts:
                            logger.info(f"开始抓取帖子评论: {post.get('title', '')[:50]}...")
                            comments = await self._get_post_comments(page, post)
                            post['comments'] = comments
                            total_comments += len(comments)
                            logger.info(f"帖子 '{post.get('title', '')[:30]}...' 抓取到 {len(comments)} 条评论")
                        
                        all_posts.extend(page_posts)
                        
                        # 检查是否有下一页
                        has_next_page = await self._go_to_next_page(page)
                        if not has_next_page:
                            logger.info("已到达最后一页")
                            break
                        
                        current_page += 1
                        await self._random_delay(2, 4)  # 页面间延迟
                        
                    except Exception as e:
                        logger.error(f"第 {current_page} 页抓取失败: {e}")
                        break
                
                logger.info(f"总共抓取 {len(all_posts)} 个精华帖子，{total_comments} 条评论，来自 {current_page} 页")
                
                # 过滤近半年的帖子
                recent_posts = self._filter_recent_half_year(all_posts)
                logger.info(f"近半年的精华帖子: {len(recent_posts)} 个")
                
                # 保存到数据库
                if recent_posts:
                    saved_posts, saved_comments = self._save_posts_with_comments(recent_posts)
                    self._log_crawl_success_with_comments(current_page, saved_posts, saved_comments)
                else:
                    logger.warning("没有找到近半年的精华帖子")
                    self._log_crawl_failure("没有找到近半年的精华帖子")
                
                # 关闭浏览器
                await browser.close()
                
                return True
                
        except Exception as e:
            logger.error(f"分页抓取精华帖子及评论失败: {e}")
            self._log_crawl_failure(str(e))
            return False
    
    async def _get_post_comments(self, page, post: Dict) -> List[Dict]:
        """获取帖子的评论和回复"""
        try:
            comments = []
            
            # 查找帖子元素并点击查看评论
            post_title = post.get('title', '')
            logger.info(f"尝试查找帖子: {post_title[:50]}...")
            
            # 查找包含帖子标题的元素
            post_elements = await page.query_selector_all(f'[class*="post"], [class*="article"], [class*="content"]')
            
            for element in post_elements:
                element_text = await element.text_content()
                if element_text and post_title[:30] in element_text:
                    logger.info(f"找到帖子元素，尝试点击查看评论")
                    
                    # 查找评论按钮
                    comment_buttons = await element.query_selector_all('[class*="comment"], [class*="reply"], button:has-text("评论"), button:has-text("查看评论")')
                    
                    for button in comment_buttons:
                        try:
                            await button.click()
                            await page.wait_for_timeout(3000)
                            logger.info("已点击评论按钮")
                            
                            # 等待评论区域加载
                            await page.wait_for_timeout(2000)
                            
                            # 获取评论内容
                            comments_content = await self._extract_comments_from_page(page)
                            comments.extend(comments_content)
                            break
                            
                        except Exception as e:
                            logger.warning(f"点击评论按钮失败: {e}")
                            continue
                    
                    break
            
            # 如果没找到评论按钮，尝试从当前页面解析评论
            if not comments:
                logger.info("未找到评论按钮，尝试从页面内容解析评论")
                comments = self._parse_comments_from_content(post.get('content', ''))
            
            return comments
            
        except Exception as e:
            logger.error(f"获取帖子评论失败: {e}")
            return []
    
    async def _extract_comments_from_page(self, page) -> List[Dict]:
        """从页面中提取评论内容"""
        try:
            comments = []
            
            # 执行JavaScript提取评论
            comments_data = await page.evaluate("""
                () => {
                    const comments = [];
                    
                    // 查找评论容器
                    const commentContainers = document.querySelectorAll('[class*="comment"], [class*="reply"], [class*="discussion"]');
                    
                    commentContainers.forEach(container => {
                        // 提取评论作者
                        const authorElement = container.querySelector('[class*="author"], [class*="user"], [class*="name"]');
                        const author = authorElement ? authorElement.textContent.trim() : '匿名用户';
                        
                        // 提取评论内容
                        const contentElement = container.querySelector('[class*="content"], [class*="text"], [class*="body"]');
                        const content = contentElement ? contentElement.textContent.trim() : container.textContent.trim();
                        
                        // 提取评论时间
                        const timeElement = container.querySelector('[class*="time"], [class*="date"], time');
                        const time = timeElement ? timeElement.textContent.trim() : '';
                        
                        // 检查是否是作者回复
                        const isAuthorReply = author.includes('金融学长') || author.includes('圈主') || author.includes('楼主');
                        
                        if (content && content.length > 5) {
                            comments.push({
                                author: author,
                                content: content,
                                date: time,
                                is_author_reply: isAuthorReply,
                                type: 'comment'
                            });
                        }
                    });
                    
                    return comments;
                }
            """)
            
            return comments_data
            
        except Exception as e:
            logger.error(f"提取评论失败: {e}")
            return []
    
    def _parse_comments_from_content(self, content: str) -> List[Dict]:
        """从帖子内容中解析评论"""
        comments = []
        
        if not content:
            return comments
        
        lines = content.split('\n')
        current_comment = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # 检测评论开始
            if self._is_comment_start(line):
                if current_comment and current_comment.get('content'):
                    comments.append(current_comment)
                
                current_comment = {
                    'author': self._extract_comment_author(line),
                    'content': '',
                    'date': datetime.now().strftime('%Y-%m-%d'),
                    'is_author_reply': self._is_author_reply(line),
                    'type': 'comment'
                }
                continue
            
            # 收集评论内容
            if current_comment:
                if not self._is_metadata_line(line) and len(line) > 5:
                    current_comment['content'] += line + '\n'
        
        # 添加最后一个评论
        if current_comment and current_comment.get('content'):
            comments.append(current_comment)
        
        return comments
    
    def _is_comment_start(self, line: str) -> bool:
        """检测是否为评论开始"""
        comment_keywords = ['回复', '评论', '说:', ':', '：']
        return any(keyword in line for keyword in comment_keywords) and len(line) > 5
    
    def _extract_comment_author(self, line: str) -> str:
        """提取评论作者"""
        # 简单的作者提取逻辑
        if ':' in line:
            return line.split(':')[0].strip()
        elif '：' in line:
            return line.split('：')[0].strip()
        else:
            return '匿名用户'
    
    def _is_author_reply(self, line: str) -> bool:
        """检测是否是作者回复"""
        author_keywords = ['金融学长', '圈主', '楼主', '作者']
        return any(keyword in line for keyword in author_keywords)
    
    async def _go_to_next_page(self, page) -> bool:
        """跳转到下一页"""
        try:
            # 查找下一页按钮
            next_selectors = [
                '.pagination .next',
                '.pagination-next',
                '.next-page',
                'a[rel="next"]',
                'button:has-text("下一页")',
                'a:has-text("下一页")'
            ]
            
            for selector in next_selectors:
                next_button = await page.query_selector(selector)
                if next_button:
                    # 检查按钮是否可点击
                    is_disabled = await next_button.get_attribute('disabled')
                    if not is_disabled:
                        await next_button.click()
                        await page.wait_for_timeout(3000)
                        logger.info("已跳转到下一页")
                        return True
            
            # 如果没有找到明确的下一页按钮，尝试滚动到底部触发加载
            logger.info("未找到明确的下一页按钮，尝试滚动触发加载")
            await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await page.wait_for_timeout(5000)
            
            # 检查是否有新内容加载
            current_content = await self._get_page_content(page)
            if len(current_content) > 1000:  # 简单检查是否有足够内容
                return True
            
            return False
            
        except Exception as e:
            logger.warning(f"跳转下一页失败: {e}")
            return False
    
    async def _scroll_page(self, page, scroll_count: int = 3):
        """滚动页面以加载更多内容"""
        for i in range(scroll_count):
            await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await self._random_delay(1, 3)
            logger.info(f"滚动页面 {i+1}/{scroll_count}")
    
    async def _get_page_content(self, page):
        """获取页面内容"""
        try:
            # 等待页面稳定
            await page.wait_for_load_state('networkidle')
            await page.wait_for_timeout(2000)
            
            # 获取页面文本内容
            content = await page.evaluate("""
                () => {
                    try {
                        // 获取页面标题
                        const title = document.title || '';
                        
                        // 获取主要文本内容
                        const mainContent = document.querySelector('.main-content, .content, .post-content, .article-content') || document.body;
                        
                        // 获取所有可见文本
                        const walker = document.createTreeWalker(
                            mainContent,
                            NodeFilter.SHOW_TEXT,
                            null,
                            false
                        );
                        
                        let textNodes = [];
                        let node;
                        while (node = walker.nextNode()) {
                            if (node.parentElement && 
                                node.parentElement.offsetParent !== null && 
                                node.textContent.trim()) {
                                textNodes.push(node.textContent.trim());
                            }
                        }
                        
                        return textNodes.join('\\n');
                    } catch (e) {
                        return '获取内容失败: ' + e.message;
                    }
                }
            """)
            
            return content
            
        except Exception as e:
            logger.error(f"获取页面内容失败: {e}")
            return ""
    
    async def _random_delay(self, min_seconds: float, max_seconds: float):
        """随机延迟，模拟人类行为"""
        delay = random.uniform(min_seconds, max_seconds)
        await asyncio.sleep(delay)
    
    def _parse_essence_posts(self, content: str) -> List[Dict]:
        """解析精华帖子内容"""
        posts = []
        
        if not content:
            return posts
        
        lines = content.split('\n')
        current_post = {}
        collecting_content = False
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # 检测精华帖子开始
            if self._is_post_start(line):
                # 保存上一个帖子
                if current_post and current_post.get('content'):
                    posts.append(current_post)
                
                # 开始新帖子
                current_post = {
                    'title': self._extract_title(line),
                    'content': '',
                    'author': '金融学长',
                    'publish_date': self._extract_date(line),
                    'likes_count': 0,
                    'comments_count': 0,
                    'view_count': 0,
                    'is_pinned': False,
                    'tags': '',
                    'summary': '',
                    'page_number': 1
                }
                collecting_content = True
                continue
            
            # 收集帖子内容
            if collecting_content and current_post:
                if not self._is_metadata_line(line):
                    if len(line) > 10:
                        current_post['content'] += line + '\n'
        
        # 添加最后一个帖子
        if current_post and current_post.get('content'):
            posts.append(current_post)
        
        return posts
    
    def _is_post_start(self, line: str) -> bool:
        """检测是否为帖子开始"""
        essence_keywords = ['精华', '【精华】', '[精华]', '置顶精华']
        return any(keyword in line for keyword in essence_keywords) and len(line) > 5
    
    def _extract_title(self, line: str) -> str:
        """提取标题"""
        title = line.replace('【精华】', '').replace('[精华]', '').replace('精华', '').strip()
        return title if title else "精华帖子"
    
    def _extract_date(self, line: str) -> str:
        """提取日期"""
        today = datetime.now()
        return today.strftime('%Y-%m-%d')
    
    def _is_metadata_line(self, line: str) -> bool:
        """检测是否为元数据行"""
        metadata_patterns = [
            '查看全文', '赞', '评论', '回复', '查看所有评论',
            '表情', '图片', '文件', '音频', '写文章', '发布'
        ]
        return any(pattern in line for pattern in metadata_patterns)
    
    def _filter_recent_half_year(self, posts: List[Dict]) -> List[Dict]:
        """过滤近半年的帖子"""
        six_months_ago = datetime.now() - timedelta(days=180)
        recent_posts = []
        
        for post in posts:
            publish_date = post.get('publish_date', '')
            if not publish_date:
                continue
            
            try:
                if '-' in publish_date:
                    post_date = datetime.strptime(publish_date, '%Y-%m-%d')
                else:
                    continue
                
                if post_date >= six_months_ago:
                    recent_posts.append(post)
                    
            except ValueError:
                continue
        
        return recent_posts
    
    def _save_posts_with_comments(self, posts: List[Dict]):
        """保存帖子及其评论到数据库"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        saved_posts = 0
        saved_comments = 0
        
        for post in posts:
            # 检查是否已存在相同标题和页码的帖子
            cursor.execute('''
                SELECT id FROM essence_posts 
                WHERE title = ? AND author = ? AND publish_date = ? AND page_number = ?
            ''', (
                post.get('title', ''), 
                post.get('author', ''), 
                post.get('publish_date', ''), 
                post.get('page_number', 1)
            ))
            
            existing = cursor.fetchone()
            
            if not existing:
                cursor.execute('''
                    INSERT INTO essence_posts (
                        title, content, author, publish_date, likes_count,
                        comments_count, view_count, is_pinned, tags, summary, page_number, post_url
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    post.get('title', ''),
                    post.get('content', ''),
                    post.get('author', ''),
                    post.get('publish_date', ''),
                    post.get('likes_count', 0),
                    post.get('comments_count', 0),
                    post.get('view_count', 0),
                    post.get('is_pinned', False),
                    post.get('tags', ''),
                    post.get('summary', ''),
                    post.get('page_number', 1),
                    post.get('post_url', '')
                ))
                post_id = cursor.lastrowid
                saved_posts += 1
                
                # 保存评论
                comments = post.get('comments', [])
                for comment in comments:
                    cursor.execute('''
                        INSERT INTO post_comments (
                            post_id, comment_author, comment_content, comment_date, 
                            is_author_reply, likes_count, comment_type
                        ) VALUES (?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        post_id,
                        comment.get('author', '匿名用户'),
                        comment.get('content', ''),
                        comment.get('date', datetime.now().strftime('%Y-%m-%d')),
                        comment.get('is_author_reply', False),
                        comment.get('likes_count', 0),
                        comment.get('type', 'comment')
                    ))
                    saved_comments += 1
        
        conn.commit()
        conn.close()
        logger.info(f"成功保存 {saved_posts} 个精华帖子和 {saved_comments} 条评论到数据库")
        return saved_posts, saved_comments
    
    def _save_essence_posts(self, posts: List[Dict]):
        """保存精华帖子到数据库"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        saved_count = 0
        for post in posts:
            # 检查是否已存在相同标题和页码的帖子
            cursor.execute('''
                SELECT id FROM essence_posts 
                WHERE title = ? AND author = ? AND publish_date = ? AND page_number = ?
            ''', (
                post.get('title', ''), 
                post.get('author', ''), 
                post.get('publish_date', ''), 
                post.get('page_number', 1)
            ))
            
            existing = cursor.fetchone()
            
            if not existing:
                cursor.execute('''
                    INSERT INTO essence_posts (
                        title, content, author, publish_date, likes_count,
                        comments_count, view_count, is_pinned, tags, summary, page_number
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    post.get('title', ''),
                    post.get('content', ''),
                    post.get('author', ''),
                    post.get('publish_date', ''),
                    post.get('likes_count', 0),
                    post.get('comments_count', 0),
                    post.get('view_count', 0),
                    post.get('is_pinned', False),
                    post.get('tags', ''),
                    post.get('summary', ''),
                    post.get('page_number', 1)
                ))
                saved_count += 1
        
        conn.commit()
        conn.close()
        logger.info(f"成功保存 {saved_count} 个精华帖子到数据库")
    
    def _log_crawl_success(self, pages_crawled: int, posts_count: int):
        """记录成功的抓取日志"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO crawl_logs (crawl_date, pages_crawled, posts_count, success, error_message)
            VALUES (?, ?, ?, ?, ?)
        ''', (datetime.now().strftime('%Y-%m-%d'), pages_crawled, posts_count, True, ''))
        
        conn.commit()
        conn.close()
    
    def _log_crawl_success_with_comments(self, pages_crawled: int, posts_count: int, comments_count: int):
        """记录成功的抓取日志（包含评论统计）"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO crawl_logs (crawl_date, pages_crawled, posts_count, comments_count, success, error_message)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (datetime.now().strftime('%Y-%m-%d'), pages_crawled, posts_count, comments_count, True, ''))
        
        conn.commit()
        conn.close()
    
    def _log_crawl_failure(self, error_message: str):
        """记录失败的抓取日志"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO crawl_logs (crawl_date, pages_crawled, posts_count, success, error_message)
            VALUES (?, ?, ?, ?, ?)
        ''', (datetime.now().strftime('%Y-%m-%d'), 0, 0, False, error_message))
        
        conn.commit()
        conn.close()
    
    def get_database_stats(self) -> Dict:
        """获取数据库统计信息"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM essence_posts')
        total_posts = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(DISTINCT page_number) FROM essence_posts')
        total_pages = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM crawl_logs WHERE success = 1')
        successful_crawls = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM crawl_logs WHERE success = 0')
        failed_crawls = cursor.fetchone()[0]
        
        # 获取最近的抓取记录
        cursor.execute('SELECT crawl_date, pages_crawled, posts_count FROM crawl_logs ORDER BY id DESC LIMIT 1')
        latest_crawl = cursor.fetchone()
        
        conn.close()
        
        stats = {
            'total_posts': total_posts,
            'total_pages': total_pages,
            'successful_crawls': successful_crawls,
            'failed_crawls': failed_crawls,
            'latest_crawl': latest_crawl
        }
        
        return stats


async def main():
    """主函数"""
    crawler = EnhancedEssenceCrawler()
    
    print("增强版小红圈精华帖子抓取系统")
    print("=" * 50)
    
    # 显示当前统计
    stats = crawler.get_database_stats()
    print(f"当前数据库统计:")
    print(f"总精华帖子数: {stats['total_posts']}")
    print(f"总抓取页数: {stats['total_pages']}")
    print(f"成功抓取次数: {stats['successful_crawls']}")
    print(f"失败抓取次数: {stats['failed_crawls']}")
    
    if stats['latest_crawl']:
        date, pages, count = stats['latest_crawl']
        print(f"最近抓取: {date} (抓取 {pages} 页, {count} 个帖子)")
    
    print("\n请选择抓取模式:")
    print("1. 仅抓取精华帖子（快速）")
    print("2. 抓取精华帖子及评论回复（完整）")
    
    choice = input("\n请输入选择 (1-2): ").strip()
    
    if choice == "1":
        print("\n开始分页抓取精华帖子...")
        print("注意: 系统将自动处理登录状态和分页加载")
        
        # 执行抓取
        success = await crawler.crawl_essence_posts_with_pagination(max_pages=10)
        
        if success:
            print("✅ 精华帖子分页抓取完成！")
            
            # 显示更新后的统计
            new_stats = crawler.get_database_stats()
            print(f"\n更新后统计:")
            print(f"总精华帖子数: {new_stats['total_posts']}")
            print(f"总抓取页数: {new_stats['total_pages']}")
            
            if new_stats['latest_crawl']:
                date, pages, count = new_stats['latest_crawl']
                print(f"本次抓取: {date} (抓取 {pages} 页, {count} 个帖子)")
            
            # 显示数据库文件信息
            db_size = os.path.getsize(crawler.db_path) if os.path.exists(crawler.db_path) else 0
            print(f"数据库文件: {crawler.db_path}")
            print(f"数据库大小: {db_size / 1024:.2f} KB")
            
            print("\n🎉 增强版系统功能演示完成！")
            
        else:
            print("❌ 精华帖子抓取失败，请检查网络连接或网站状态")
    
    elif choice == "2":
        print("\n开始分页抓取精华帖子及评论...")
        print("注意: 系统将自动处理登录状态和分页加载")
        print("⚠️  评论抓取可能需要较长时间，请耐心等待")
        
        # 执行抓取
        success = await crawler.crawl_essence_posts_with_comments(max_pages=5)  # 先测试5页
        
        if success:
            print("✅ 精华帖子及评论分页抓取完成！")
            
            # 显示更新后的统计
            new_stats = crawler.get_database_stats()
            print(f"\n更新后统计:")
            print(f"总精华帖子数: {new_stats['total_posts']}")
            print(f"总抓取页数: {new_stats['total_pages']}")
            
            # 获取评论统计
            conn = sqlite3.connect(crawler.db_path)
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM post_comments')
            total_comments = cursor.fetchone()[0]
            conn.close()
            
            print(f"总评论数: {total_comments}")
            
            if new_stats['latest_crawl']:
                date, pages, count = new_stats['latest_crawl']
                print(f"本次抓取: {date} (抓取 {pages} 页, {count} 个帖子)")
            
            # 显示数据库文件信息
            db_size = os.path.getsize(crawler.db_path) if os.path.exists(crawler.db_path) else 0
            print(f"数据库文件: {crawler.db_path}")
            print(f"数据库大小: {db_size / 1024:.2f} KB")
            
            print("\n🎉 增强版系统功能演示完成！")
            
        else:
            print("❌ 精华帖子及评论抓取失败，请检查网络连接或网站状态")
    
    else:
        print("❌ 无效选择，程序退出")


if __name__ == "__main__":
    asyncio.run(main())
