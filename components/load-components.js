// 动态加载公共组件
async function loadComponent(elementId, componentPath) {
    try {
        const response = await fetch(componentPath);
        if (response.ok) {
            const html = await response.text();
            const element = document.getElementById(elementId);
            if (element) {
                element.outerHTML = html;
            }
        }
    } catch (error) {
        console.log(`Failed to load ${componentPath}:`, error);
    }
}

// 页面加载完成后加载所有组件
document.addEventListener('DOMContentLoaded', function() {
    // 获取当前页面相对于根目录的路径
    const path = window.location.pathname;
    const isInPosts = path.includes('/posts/') || path.includes('\\posts\\');
    
    // 根据页面位置设置组件路径
    const basePath = isInPosts ? '../components/' : 'components/';
    
    // 加载导航栏和页脚
    loadComponent('navbar-placeholder', basePath + 'navbar.html');
    loadComponent('footer-placeholder', basePath + 'footer.html');
});
