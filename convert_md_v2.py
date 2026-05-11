#!/usr/bin/env python3
"""
更好的 Markdown 转 HTML 转换器
"""

import re

def convert_markdown_to_html(md_text):
    lines = md_text.split('\n')
    html_lines = []
    in_code_block = False
    code_content = []
    
    i = 0
    while i < len(lines):
        line = lines[i]
        
        # 代码块开始
        if line.strip().startswith('```'):
            if not in_code_block:
                in_code_block = True
                code_content = []
                i += 1
                continue
            else:
                # 代码块结束
                html_lines.append('<pre><code>')
                html_lines.extend(code_content)
                html_lines.append('</code></pre>')
                in_code_block = False
                i += 1
                continue
        
        if in_code_block:
            code_content.append(line)
            i += 1
            continue
        
        # 标题
        if line.startswith('# '):
            html_lines.append(f'<h1>{line[2:]}</h1>')
            i += 1
            continue
        if line.startswith('## '):
            html_lines.append(f'<h2>{line[3:]}</h2>')
            i += 1
            continue
        if line.startswith('### '):
            html_lines.append(f'<h3>{line[4:]}</h3>')
            i += 1
            continue
        
        # 空行
        if not line.strip():
            html_lines.append('')
            i += 1
            continue
        
        # 普通段落 - 收集连续的非空行
        paragraph = []
        while i < len(lines) and lines[i].strip() and not lines[i].strip().startswith('```') and not lines[i].startswith('#') and not lines[i].startswith('|'):
            # 处理内联代码
            line_processed = re.sub(r'`([^`]+)`', r'<code>\1</code>', lines[i])
            # 处理粗体
            line_processed = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', line_processed)
            paragraph.append(line_processed)
            i += 1
        
        if paragraph:
            html_lines.append('<p>' + ' '.join(paragraph) + '</p>')
    
    return '\n'.join(html_lines)


# 读取 Markdown
with open(r'C:\Users\Administrator\Downloads\LangGraph_LangChain_学习笔记.md', 'r', encoding='utf-8') as f:
    md_content = f.read()

# 转成 HTML 内容
body_html = convert_markdown_to_html(md_content)

# 完整 HTML 模板
template = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>LangGraph 与 LangChain 学习笔记 | PGH Blog</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="styles.css">
    <style>
        .post-header { padding: 160px 24px 60px; background: radial-gradient(circle at 50% 0%, rgba(59, 130, 246, 0.15) 0%, transparent 50%), var(--bg-primary); }
        .post-container { max-width: 800px; margin: 0 auto; }
        .post-title { font-size: 42px; font-weight: 700; line-height: 1.3; margin-bottom: 24px; }
        .post-meta { display: flex; align-items: center; gap: 16px; margin-bottom: 32px; flex-wrap: wrap; }
        .post-category { padding: 6px 16px; background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%); color: white; border-radius: 20px; font-size: 13px; font-weight: 600; }
        .post-date { color: var(--text-tertiary); font-size: 15px; }
        .post-content { padding: 40px 24px 80px; }
        .post-content h2 { font-size: 28px; font-weight: 600; margin: 40px 0 20px; color: var(--text-primary); }
        .post-content h3 { font-size: 22px; font-weight: 600; margin: 32px 0 16px; color: var(--text-primary); }
        .post-content p { color: var(--text-secondary); line-height: 1.8; margin-bottom: 20px; font-size: 17px; }
        .post-content ul { color: var(--text-secondary); line-height: 1.8; margin-bottom: 20px; padding-left: 24px; }
        .post-content ol { color: var(--text-secondary); line-height: 1.8; margin-bottom: 20px; padding-left: 24px; }
        .post-content li { margin-bottom: 12px; font-size: 17px; }
        .post-content code { background: var(--bg-secondary); padding: 2px 8px; border-radius: 6px; font-family: 'JetBrains Mono', monospace; font-size: 14px; color: #3b82f6; }
        .post-content pre { background: var(--code-bg); padding: 24px; border-radius: 12px; overflow-x: auto; margin-bottom: 24px; }
        .post-content pre code { background: none; padding: 0; color: #e2e8f0; }
        .post-content blockquote { border-left: 4px solid #3b82f6; padding-left: 20px; margin: 24px 0; color: var(--text-tertiary); font-style: italic; }
        .back-btn { display: inline-flex; align-items: center; gap: 8px; color: #3b82f6; text-decoration: none; font-weight: 500; margin-bottom: 32px; transition: transform 0.3s ease; }
        .back-btn:hover { transform: translateX(-4px); }
        .architecture-box { background: rgba(59, 130, 246, 0.05); border: 1px solid rgba(59, 130, 246, 0.2); border-radius: 12px; padding: 24px; margin: 24px 0; font-family: 'JetBrains Mono', monospace; font-size: 14px; line-height: 1.6; color: var(--text-secondary); }
        .highlight-quote { background: linear-gradient(135deg, rgba(59, 130, 246, 0.1), rgba(168, 85, 247, 0.1)); border-radius: 16px; padding: 24px; margin: 32px 0; text-align: center; font-size: 18px; font-weight: 500; color: var(--text-primary); }
        @media (max-width: 768px) { .post-title { font-size: 32px; } }
    </style>
</head>
<body>
    <div class="theme-toggle" id="themeToggle">
        <svg class="sun-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="5"></circle><line x1="12" y1="1" x2="12" y2="3"></line><line x1="12" y1="21" x2="12" y2="23"></line></svg>
        <svg class="moon-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"></path></svg>
    </div>
    <nav class="navbar">
        <div class="nav-container">
            <a href="../index.html" class="logo">PGH<span class="dot">.</span></a>
            <ul class="nav-links">
                <li><a href="../index.html">首页</a></li>
                <li><a href="../blog.html">博客</a></li>
                <li><a href="../projects.html">项目</a></li>
            </ul>
            <div class="hamburger"><span></span><span></span><span></span></div>
        </div>
    </nav>
    <section class="post-header">
        <div class="post-container">
            <a href="../blog.html" class="back-btn"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="width: 20px; height: 20px;"><polyline points="15 18 9 12 15 6"></polyline></svg>返回博客列表</a>
            <h1 class="post-title">LangGraph 与 LangChain 学习笔记</h1>
            <div class="post-meta"><span class="post-category">AI 开发</span><span class="post-date">2026年5月11日</span></div>
        </div>
    </section>
    <article class="post-content">
        <div class="post-container">
            BODY_CONTENT
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
                        <a href="../index.html">首页</a>
                        <a href="../blog.html">博客</a>
                        <a href="../projects.html">项目</a>
                    </div>
                    <div class="footer-column">
                        <h4>社交</h4>
                        <a href="https://github.com/PGH11" target="_blank">GitHub</a>
                    </div>
                </div>
            </div>
            <div class="footer-bottom">
                <p>© 2024 PGH. All rights reserved. Built with ❤️</p>
            </div>
        </div>
    </footer>
    <script src="../script.js"></script>
</body>
</html>"""

# 替换内容
final_html = template.replace('BODY_CONTENT', body_html)

# 写入文件
output_path = r'C:\Users\Administrator\.qwenpaw\workspaces\default\personal-blog\posts\langgraph-langchain-learning-notes.html'
with open(output_path, 'w', encoding='utf-8') as f:
    f.write(final_html)

print(f'✅ Created: {output_path}')
print(f'📊 File size: {len(final_html)} bytes')
