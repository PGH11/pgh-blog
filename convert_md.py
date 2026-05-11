import re

def markdown_to_html(md_text):
    """简单的 Markdown 转 HTML"""
    
    # 代码块
    md_text = re.sub(r'```python\n(.*?)```', r'<pre><code>\1</code></pre>', md_text, flags=re.DOTALL)
    md_text = re.sub(r'```json\n(.*?)```', r'<pre><code>\1</code></pre>', md_text, flags=re.DOTALL)
    md_text = re.sub(r'```\n(.*?)```', r'<pre><code>\1</code></pre>', md_text, flags=re.DOTALL)
    
    # 内联代码
    md_text = re.sub(r'`([^`]+)`', r'<code>\1</code>', md_text)
    
    # 标题
    md_text = re.sub(r'^## (.*?)$', r'<h2>\1</h2>', md_text, flags=re.MULTILINE)
    md_text = re.sub(r'^### (.*?)$', r'<h3>\1</h3>', md_text, flags=re.MULTILINE)
    md_text = re.sub(r'^# (.*?)$', r'<h1>\1</h1>', md_text, flags=re.MULTILINE)
    
    # 粗体
    md_text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', md_text)
    
    # 列表
    md_text = re.sub(r'^- (.*?)$', r'<li>\1</li>', md_text, flags=re.MULTILINE)
    md_text = re.sub(r'^\d+\. (.*?)$', r'<li>\1</li>', md_text, flags=re.MULTILINE)
    
    # 段落（把连续的文本行包裹成 p）
    lines = md_text.split('\n')
    in_paragraph = False
    result = []
    
    for line in lines:
        stripped = line.strip()
        if not stripped:
            if in_paragraph:
                result.append('</p>')
                in_paragraph = False
            result.append('')
        elif stripped.startswith('<'):
            if in_paragraph:
                result.append('</p>')
                in_paragraph = False
            result.append(line)
        else:
            if not in_paragraph:
                result.append('<p>')
                in_paragraph = True
            result.append(line)
    
    if in_paragraph:
        result.append('</p>')
    
    return '\n'.join(result)

# 读取 Markdown
with open(r'C:\Users\Administrator\Downloads\LangGraph_LangChain_学习笔记.md', 'r', encoding='utf-8') as f:
    md_content = f.read()

# 转成 HTML 内容
body_html = markdown_to_html(md_content)

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
    <link rel="stylesheet" href="https://pgh11.github.io/pgh-blog/styles.css">
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
            <a href="https://pgh11.github.io/pgh-blog/index.html" class="logo">PGH<span class="dot">.</span></a>
            <ul class="nav-links"></ul>
            <div class="hamburger"><span></span><span></span><span></span></div>
        </div>
    </nav>
    <section class="post-header">
        <div class="post-container">
            <a href="https://pgh11.github.io/pgh-blog/blog.html" class="back-btn"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="width: 20px; height: 20px;"><polyline points="15 18 9 12 15 6"></polyline></svg>返回博客列表</a>
            <h1 class="post-title">LangGraph 与 LangChain 学习笔记</h1>
            <div class="post-meta"><span class="post-category">AI 开发</span><span class="post-date">2026年5月11日</span></div>
        </div>
    </section>
    <article class="post-content">
        <div class="post-container">
            BODY_CONTENT
        </div>
    </article>
    <script src="script.js"></script>
</body>
</html>"""

# 替换内容
final_html = template.replace('BODY_CONTENT', body_html)

# 写入文件
output_path = r'C:\Users\Administrator\.qwenpaw\workspaces\default\personal-blog\posts\langgraph-langchain-learning-notes.html'
with open(output_path, 'w', encoding='utf-8') as f:
    f.write(final_html)

print(f'Created: {output_path}')
