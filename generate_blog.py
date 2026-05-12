#!/usr/bin/env python3
"""Markdown 转 HTML 博客文章"""

import re

def convert_md_to_blog_html(md_text, title, category, date, filename):
    """把 Markdown 转成博客 HTML"""
    
    # 1. 提取代码块，临时替换
    code_blocks = []
    
    def save_code_block(match):
        code_blocks.append(match.group(1))
        return f'%%CODE_BLOCK_{len(code_blocks)-1}%%'
    
    md_text = re.sub(r'```(\w*)\n(.*?)```', save_code_block, md_text, flags=re.DOTALL)
    
    # 2. 处理内联代码
    md_text = re.sub(r'`([^`]+)`', r'<code>\1</code>', md_text)
    
    # 3. 处理粗体
    md_text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', md_text)
    
    # 4. 处理标题
    md_text = re.sub(r'^### (.*?)$', r'<h3>\1</h3>', md_text, flags=re.MULTILINE)
    md_text = re.sub(r'^## (.*?)$', r'<h2>\1</h2>', md_text, flags=re.MULTILINE)
    md_text = re.sub(r'^# (.*?)$', r'<h2>\1</h2>', md_text, flags=re.MULTILINE)
    
    # 5. 处理列表
    md_text = re.sub(r'^- (.*?)$', r'<li>\1</li>', md_text, flags=re.MULTILINE)
    md_text = re.sub(r'^\d+\. (.*?)$', r'<li>\1</li>', md_text, flags=re.MULTILINE)
    
    # 6. 处理段落
    lines = md_text.split('\n')
    result = []
    in_list = False
    
    for line in lines:
        stripped = line.strip()
        
        # 列表项
        if stripped.startswith('<li>'):
            if not in_list:
                result.append('<ul>')
                in_list = True
            result.append(stripped)
            continue
        
        # 列表结束
        if in_list and not stripped.startswith('<li>'):
            result.append('</ul>')
            in_list = False
        
        # 已有 HTML 标签的行
        if stripped.startswith('<'):
            result.append(stripped)
            continue
        
        # 空行
        if not stripped:
            result.append('')
            continue
        
        # 普通段落
        result.append(f'<p>{stripped}</p>')
    
    if in_list:
        result.append('</ul>')
    
    body_html = '\n'.join(result)
    
    # 7. 还原代码块
    for i, code in enumerate(code_blocks):
        # HTML 转义
        code_escaped = code.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        body_html = body_html.replace(
            f'%%CODE_BLOCK_{i}%%',
            f'<pre><code>{code_escaped}</code></pre>'
        )
    
    # 8. 生成完整 HTML
    template = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} | PGH Blog</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://pgh11.github.io/pgh-blog/styles.css">
    <style>
        .post-header {{ padding: 160px 24px 60px; background: radial-gradient(circle at 50% 0%, rgba(59, 130, 246, 0.15) 0%, transparent 50%), var(--bg-primary); }}
        .post-container {{ max-width: 800px; margin: 0 auto; }}
        .post-title {{ font-size: 42px; font-weight: 700; line-height: 1.3; margin-bottom: 24px; }}
        .post-meta {{ display: flex; align-items: center; gap: 16px; margin-bottom: 32px; flex-wrap: wrap; }}
        .post-category {{ padding: 6px 16px; background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%); color: white; border-radius: 20px; font-size: 13px; font-weight: 600; }}
        .post-date {{ color: var(--text-tertiary); font-size: 15px; }}
        .post-content {{ padding: 40px 24px 80px; }}
        .post-content h2 {{ font-size: 28px; font-weight: 600; margin: 40px 0 20px; color: var(--text-primary); }}
        .post-content h3 {{ font-size: 22px; font-weight: 600; margin: 32px 0 16px; color: var(--text-primary); }}
        .post-content p {{ color: var(--text-secondary); line-height: 1.8; margin-bottom: 20px; font-size: 17px; }}
        .post-content ul {{ color: var(--text-secondary); line-height: 1.8; margin-bottom: 20px; padding-left: 24px; }}
        .post-content ol {{ color: var(--text-secondary); line-height: 1.8; margin-bottom: 20px; padding-left: 24px; }}
        .post-content li {{ margin-bottom: 12px; font-size: 17px; }}
        .post-content code {{ background: var(--bg-secondary); padding: 2px 8px; border-radius: 6px; font-family: 'JetBrains Mono', monospace; font-size: 14px; color: #3b82f6; }}
        .post-content pre {{ background: var(--bg-secondary); padding: 20px; border-radius: 12px; overflow-x: auto; margin-bottom: 24px; }}
        .post-content pre code {{ background: none; padding: 0; color: var(--text-primary); font-size: 14px; line-height: 1.8; }}
        .post-content blockquote {{ border-left: 4px solid #3b82f6; padding-left: 20px; margin: 24px 0; color: var(--text-tertiary); font-style: italic; }}
        .back-btn {{ display: inline-flex; align-items: center; gap: 8px; color: #3b82f6; text-decoration: none; font-weight: 500; margin-bottom: 32px; transition: transform 0.3s ease; }}
        .back-btn:hover {{ transform: translateX(-4px); }}
        @media (max-width: 768px) {{ .post-title {{ font-size: 32px; }} }}
    </style>
</head>
<body>
    <div class="theme-toggle" id="themeToggle">
        <svg class="sun-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="5"></circle><line x1="12" y1="1" x2="12" y2="3"></line><line x1="12" y1="21" x2="12" y2="23"></line></svg>
        <svg class="moon-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"></path></svg>
    </div>
    <nav class="navbar">
        <div class="nav-container">
            <a href="https://pgh11.github.io/pgh-blog/index.html" class="logo">PGH<span class="dot">.</span></a>
            <ul class="nav-links">
                <li><a href="https://pgh11.github.io/pgh-blog/index.html">首页</a></li>
                <li><a href="https://pgh11.github.io/pgh-blog/blog.html" class="active">博客</a></li>
                <li><a href="https://pgh11.github.io/pgh-blog/projects.html">项目</a></li>
            </ul>
            <div class="hamburger"><span></span><span></span><span></span></div>
        </div>
    </nav>
    <section class="post-header">
        <div class="post-container">
            <a href="https://pgh11.github.io/pgh-blog/blog.html" class="back-btn"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="width: 20px; height: 20px;"><polyline points="15 18 9 12 15 6"></polyline></svg>返回博客列表</a>
            <h1 class="post-title">{title}</h1>
            <div class="post-meta"><span class="post-category">{category}</span><span class="post-date">{date}</span></div>
        </div>
    </section>
    <article class="post-content">
        <div class="post-container">
            {body_html}
        </div>
    </article>
    <footer class="footer">
        <div class="footer-container">
            <div class="footer-content">
                <div class="footer-brand">
                    <span class="logo">PGH<span class="dot">.</span></span>
                    <p class="footer-tagline">用代码保障质量，用测试守护体验</p>
                </div>
                <div class="footer-links">
                    <div class="footer-column">
                        <h4>导航</h4>
                        <a href="https://pgh11.github.io/pgh-blog/index.html">首页</a>
                        <a href="https://pgh11.github.io/pgh-blog/blog.html">博客</a>
                        <a href="https://pgh11.github.io/pgh-blog/projects.html">项目</a>
                    </div>
                    <div class="footer-column">
                        <h4>社交</h4>
                        <a href="https://github.com/PGH11" target="_blank">GitHub</a>
                    </div>
                </div>
            </div>
            <div class="footer-bottom">
                <p>&copy; 2024 PGH. All rights reserved. Built with &#10084;&#65039;</p>
            </div>
        </div>
    </footer>
    <script src="https://pgh11.github.io/pgh-blog/script.js"></script>
</body>
</html>'''
    
    # 写入文件
    output_path = f'C:\\Users\\Administrator\\.qwenpaw\\workspaces\\default\\personal-blog\\posts\\{filename}'
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(template)
    
    print(f'Created: {output_path} ({len(template)} bytes)')


# ===== 生成两篇博客 =====

# 1. LangGraph 与 LangChain 学习笔记
with open(r'C:\Users\Administrator\.qwenpaw\workspaces\default\agent-learning-notes\docs\LangGraph_LangChain_学习笔记.md', 'r', encoding='utf-8') as f:
    md1 = f.read()
convert_md_to_blog_html(
    md1,
    title='LangGraph 与 LangChain 学习笔记',
    category='AI 开发',
    date='2026年5月12日',
    filename='langgraph-langchain-learning-notes.html'
)

# 2. LangSmith 测试经验
with open(r'C:\Users\Administrator\.qwenpaw\workspaces\default\agent-learning-notes\docs\LangSmith_测试经验.md', 'r', encoding='utf-8') as f:
    md2 = f.read()
convert_md_to_blog_html(
    md2,
    title='LangSmith 测试经验：Agent 追踪与排查实战',
    category='AI 测试',
    date='2026年5月12日',
    filename='langsmith-testing-experience.html'
)

print('All done!')
