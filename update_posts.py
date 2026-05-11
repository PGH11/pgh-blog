import re

def process_file(src_path, dest_path):
    # 用 UTF-8 读取源文件
    with open(src_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 移除导航栏的关于链接
    content = re.sub(r'<li><a href=["\'].*?about\.html["\']>关于</a></li>', '', content)
    # 移除页脚的关于链接
    content = re.sub(r'<a href=["\'].*?about\.html["\']>关于</a>', '', content)
    
    # 用 UTF-8 写入目标文件
    with open(dest_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f'Processed: {dest_path}')

# 处理 Fiddler 文章
process_file(
    r'C:\Users\Administrator\Downloads\fiddler-mumu-android-capture-blog - 副本.txt',
    r'C:\Users\Administrator\.qwenpaw\workspaces\default\personal-blog\posts\fiddler-mumu-android-capture.html'
)

# 处理 AI 模型监控文章
process_file(
    r'C:\Users\Administrator\Downloads\forum_implementation_plan.txt',
    r'C:\Users\Administrator\.qwenpaw\workspaces\default\personal-blog\posts\ai-model-monitoring-closed-loop.html'
)

print('Done!')
