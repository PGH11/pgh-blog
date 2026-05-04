# PGH 个人技术博客

基于现代化设计的个人技术博客，专注于测试自动化、框架设计和质量保障领域。

## ✨ 特性

- 🎨 **现代化设计** - 采用渐变配色、玻璃拟态效果，支持深色/浅色主题切换
- 📱 **响应式布局** - 完美适配桌面、平板、手机等各种设备
- ⚡ **流畅动画** - 滚动动画、悬停效果、平滑过渡，提升用户体验
- 🌙 **主题切换** - 支持深色/浅色模式，自动跟随系统偏好
- 📝 **博客系统** - 分类过滤、文章卡片，支持后续扩展
- 🚀 **项目展示** - 精心设计的项目展示页面，突出开源项目
- 📊 **技术栈展示** - 可视化的技能分类展示
- 📱 **移动端导航** - 汉堡菜单，适配小屏设备

## 📁 项目结构

```
personal-blog/
├── index.html          # 首页
├── blog.html           # 博客列表页
├── projects.html       # 项目展示页
├── about.html          # 关于页面
├── styles.css          # 全局样式
├── script.js           # 交互脚本
└── README.md           # 说明文档
```

## 🚀 快速开始

### 方式一：直接打开

直接用浏览器打开 `index.html` 文件即可预览网站效果。

### 方式二：本地服务器（推荐）

使用 Python 启动本地服务器：

```bash
cd personal-blog
python -m http.server 8080
```

然后在浏览器中访问 `http://localhost:8080`

使用 Node.js：

```bash
cd personal-blog
npx serve -p 8080
```

## 🎨 设计亮点

### 色彩系统
- **主色调**：紫色渐变 (#6366f1 → #8b5cf6)
- **背景色**：浅色/深色双主题
- **语义色**：成功绿、警告黄、错误红
- **文本层级**：三级文本色，保证可读性

### 排版系统
- **字体**：Inter 无衬线字体 + JetBrains Mono 等宽字体
- **层级**：清晰的标题、正文、辅助文本层级
- **行高**：优化的阅读体验

### 动效设计
- 滚动渐入动画
- 悬停上浮效果
- 平滑过渡动画
- 代码窗口 3D 透视效果

## 🔧 自定义配置

### 修改个人信息

编辑 `index.html` 中的以下部分：

```html
<h1 class="name">PGH</h1>           <!-- 你的名字 -->
<p class="bio">...</p>              <!-- 个人简介 -->
<a href="..." class="social-link">  <!-- 社交链接 -->
```

### 添加博客文章

在 `blog.html` 中复制 `.blog-card` 模板，修改内容即可添加新文章。

### 添加新项目

在 `projects.html` 中复制 `.project-card` 模板，配置项目信息。

### 修改主题色

编辑 `styles.css` 中的 CSS 变量：

```css
:root {
    --accent-primary: #6366f1;      /* 主色调 */
    --accent-secondary: #8b5cf6;    /* 辅助色 */
}
```

## 📱 浏览器支持

- ✅ Chrome (推荐)
- ✅ Firefox
- ✅ Safari
- ✅ Edge

## 🚢 部署建议

### GitHub Pages

1. 将 `personal-blog` 目录内容推送到 GitHub 仓库
2. 在仓库设置中开启 GitHub Pages
3. 选择 `main` 分支作为源
4. 访问 `https://yourname.github.io/repo-name`

### Vercel / Netlify

直接导入仓库，一键部署，支持自动 HTTPS 和 CDN。

### Nginx

将文件上传到服务器，配置 Nginx 静态文件服务：

```nginx
server {
    listen 80;
    server_name yourdomain.com;
    root /path/to/personal-blog;
    index index.html;
}
```

## 📄 许可证

MIT License - 可自由使用和修改

---

**Built with ❤️ by PGH** | 用代码保障质量，用测试守护体验