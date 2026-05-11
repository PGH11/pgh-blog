import re

with open(r'posts/langgraph-langchain-learning-notes.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 查找所有代码块
def fix_code_blocks(match):
    code = match.group(1).strip()
    lines = code.split('\n')
    
    # 如果是短文本，且包含中文，大概率不是代码，改成普通文本
    has_chinese = any('\u4e00' <= c <= '\u9fff' for c in code)
    
    if has_chinese and len(lines) <= 8:
        # 把每行用 <br> 连接
        text = '<br>'.join(lines)
        return f'<p style="font-family: JetBrains Mono, monospace; background: var(--bg-secondary); padding: 20px; border-radius: 12px; font-size: 14px; line-height: 2;">{text}</p>'
    
    return match.group(0)

content = re.sub(r'<pre><code>(.*?)</code></pre>', fix_code_blocks, content, flags=re.DOTALL)

with open(r'posts/langgraph-langchain-learning-notes.html', 'w', encoding='utf-8') as f:
    f.write(content)

print('Fixed code blocks!')
