import re

with open(r'posts/langgraph-langchain-learning-notes.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 清理所有错误的代码块标签
content = re.sub(r'</code></pre>text', '', content)
content = re.sub(r'</code></pre>', '', content)
content = re.sub(r'<pre><code>', '', content)
content = re.sub(r'``<code>', '', content)

with open(r'posts/langgraph-langchain-learning-notes.html', 'w', encoding='utf-8') as f:
    f.write(content)

print('Cleaned up!')
