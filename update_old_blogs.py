#!/usr/bin/env python3
"""重新生成 LangSmith 和 LangGraph 两篇博客 HTML（只替换正文部分）"""

import re

def convert_md_to_body_html(md_text):
    """把 Markdown 转成 HTML body 内容（不包含页面框架）"""
    
    code_blocks = []
    def save_code_block(match):
        code_blocks.append(match.group(2))
        return f'%%CODE_BLOCK_{len(code_blocks)-1}%%'
    md_text = re.sub(r'```(\w*)\n(.*?)```', save_code_block, md_text, flags=re.DOTALL)
    
    md_text = re.sub(r'`([^`]+)`', r'<code>\1</code>', md_text)
    md_text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', md_text)
    md_text = re.sub(r'^### (.*?)$', r'<h3>\1</h3>', md_text, flags=re.MULTILINE)
    md_text = re.sub(r'^## (.*?)$', r'<h2>\1</h2>', md_text, flags=re.MULTILINE)
    md_text = re.sub(r'^# (.*?)$', r'<h2>\1</h2>', md_text, flags=re.MULTILINE)
    md_text = re.sub(r'^- (.*?)$', r'<li>\1</li>', md_text, flags=re.MULTILINE)
    md_text = re.sub(r'^\d+\. (.*?)$', r'<li>\1</li>', md_text, flags=re.MULTILINE)
    md_text = re.sub(r'^\|.*\|$', '', md_text, flags=re.MULTILINE)
    
    lines = md_text.split('\n')
    result = []
    in_list = False
    for line in lines:
        stripped = line.strip()
        if stripped.startswith('<li>'):
            if not in_list:
                result.append('<ul>')
                in_list = True
            result.append(stripped)
            continue
        if in_list and not stripped.startswith('<li>'):
            result.append('</ul>')
            in_list = False
        if stripped.startswith('<'):
            result.append(stripped)
            continue
        if not stripped:
            result.append('')
            continue
        result.append(f'<p>{stripped}</p>')
    if in_list:
        result.append('</ul>')
    
    body_html = '\n'.join(result)
    for i, code in enumerate(code_blocks):
        code_escaped = code.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        body_html = body_html.replace(f'%%CODE_BLOCK_{i}%%', f'<pre><code>{code_escaped}</code></pre>')
    
    return body_html


def replace_article_content(html_path, new_body_html):
    """替换 HTML 文件中 <article> 到 </article> 之间的正文内容"""
    with open(html_path, 'r', encoding='utf-8') as f:
        html = f.read()
    
    # 找到 <article> 和 </article> 的位置
    article_start = html.index('<article class="post-content">')
    article_end = html.index('</article>') + len('</article>')
    
    prefix = html[:article_start]
    suffix = html[article_end:]
    
    new_article = f'''    <article class="post-content">
        <div class="post-container">
            {new_body_html}
        </div>
    </article>'''
    
    new_html = prefix + new_article + suffix
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(new_html)
    
    print(f'Updated: {html_path} (new size: {len(new_html)} bytes)')


# ===== 1. LangSmith =====
with open(r'E:\project\agent_test\LangSmith_测试经验.md', 'r', encoding='utf-8') as f:
    md1 = f.read()
body1 = convert_md_to_body_html(md1)
replace_article_content(
    r'C:\Users\Administrator\.qwenpaw\workspaces\default\personal-blog\posts\langsmith-testing-experience.html',
    body1,
)

# ===== 2. LangGraph =====
with open(r'E:\project\agent_test\LangGraph_LangChain_学习笔记.md', 'r', encoding='utf-8') as f:
    md2 = f.read()
body2 = convert_md_to_body_html(md2)
replace_article_content(
    r'C:\Users\Administrator\.qwenpaw\workspaces\default\personal-blog\posts\langgraph-langchain-learning-notes.html',
    body2,
)

print('All done!')
