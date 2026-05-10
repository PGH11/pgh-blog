// 公共组件 - 导航栏
const navbarHTML = `
    <nav class="navbar">
        <div class="nav-container">
            <a href="INDEX_PATH" class="logo">PGH<span class="dot">.</span></a>
            <ul class="nav-links">
                <li><a href="INDEX_PATH">首页</a></li>
                <li><a href="BLOG_PATH">博客</a></li>
                <li><a href="PROJECTS_PATH">项目</a></li>
            </ul>
            <div class="hamburger">
                <span></span>
                <span></span>
                <span></span>
            </div>
        </div>
    </nav>
`;

// 公共组件 - 页脚
const footerHTML = `
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
                        <a href="INDEX_PATH">首页</a>
                        <a href="BLOG_PATH">博客</a>
                        <a href="PROJECTS_PATH">项目</a>
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
`;

// 加载组件
function loadComponents() {
    // 判断是否在 posts 目录下
    const path = window.location.pathname;
    const isInPosts = path.includes('/posts/') || path.includes('\\posts\\');
    
    // 设置正确的路径前缀
    const prefix = isInPosts ? '../' : '';
    
    // 替换路径占位符
    const navbar = navbarHTML
        .replace(/INDEX_PATH/g, prefix + 'index.html')
        .replace(/BLOG_PATH/g, prefix + 'blog.html')
        .replace(/PROJECTS_PATH/g, prefix + 'projects.html');
    
    const footer = footerHTML
        .replace(/INDEX_PATH/g, prefix + 'index.html')
        .replace(/BLOG_PATH/g, prefix + 'blog.html')
        .replace(/PROJECTS_PATH/g, prefix + 'projects.html');
    
    // 插入到页面
    const navbarPlaceholder = document.getElementById('navbar-placeholder');
    const footerPlaceholder = document.getElementById('footer-placeholder');
    
    if (navbarPlaceholder) {
        navbarPlaceholder.outerHTML = navbar;
    }
    
    if (footerPlaceholder) {
        footerPlaceholder.outerHTML = footer;
    }
    
    // 设置当前页面的 active 状态
    setTimeout(setActiveNav, 100);
}

// 设置导航栏 active 状态
function setActiveNav() {
    const currentPage = window.location.pathname.split('/').pop();
    const navLinks = document.querySelectorAll('.nav-links a');
    
    navLinks.forEach(link => {
        const linkPage = link.getAttribute('href').split('/').pop();
        if (linkPage === currentPage) {
            link.classList.add('active');
        }
    });
}

// 页面加载完成后执行
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', loadComponents);
} else {
    loadComponents();
}
