import os
import re

posts_dir = 'posts'

for filename in os.listdir(posts_dir):
    if filename.endswith('.html'):
        filepath = os.path.join(posts_dir, filename)
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 移除导航栏的关于链接
        content = re.sub(r'<li><a href=["\'].*?about\.html["\']>关于</a></li>', '', content)
        # 移除页脚的关于链接
        content = re.sub(r'<a href=["\'].*?about\.html["\']>关于</a>', '', content)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f'Fixed: {filename}')

print('Done!')
