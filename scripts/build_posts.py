#!/usr/bin/env python3
"""Build blog HTML pages from Markdown sources in posts-md/."""

from __future__ import annotations

import html
import re
import textwrap
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Any

import markdown
import yaml


ROOT = Path(__file__).resolve().parents[1]
POSTS_MD_DIR = ROOT / "posts-md"
POSTS_DIR = ROOT / "posts"
BLOG_HTML = ROOT / "blog.html"
INDEX_HTML = ROOT / "index.html"

COLORS = [
    ("#3b82f6", "#0f766e"),
    ("#f59e0b", "#d97706"),
    ("#10b981", "#059669"),
    ("#ec4899", "#be185d"),
    ("#8b5cf6", "#6d28d9"),
    ("#f97316", "#ea580c"),
]


@dataclass
class Post:
    title: str
    slug: str
    date: date
    category: str
    summary: str
    body_html: str
    href: str

    @property
    def display_date(self) -> str:
        return f"{self.date.year}年{self.date.month}月{self.date.day}日"

    @property
    def compact_date(self) -> str:
        return self.date.strftime("%Y.%m.%d")


def main() -> None:
    POSTS_DIR.mkdir(exist_ok=True)
    posts = sorted(read_posts(), key=lambda item: item.date, reverse=True)
    for post in posts:
        write_post_html(post)
    update_blog_index(posts)
    update_home_recent_posts(posts)
    print(f"Built {len(posts)} Markdown post(s).")


def read_posts() -> list[Post]:
    posts: list[Post] = []
    for md_path in sorted(POSTS_MD_DIR.glob("*.md")):
        text = md_path.read_text(encoding="utf-8").lstrip("\ufeff")
        metadata, body_md = split_frontmatter(text)
        title = required_str(metadata, "title", md_path)
        slug = str(metadata.get("slug") or md_path.stem).strip()
        post_date = parse_date(metadata.get("date"), md_path)
        category = str(metadata.get("category") or first_tag(metadata) or "博客").strip()
        summary = str(metadata.get("summary") or "").strip()
        body_html = markdown_to_html(body_md)
        posts.append(
            Post(
                title=title,
                slug=slug,
                date=post_date,
                category=category,
                summary=summary,
                body_html=body_html,
                href=f"posts/{slug}.html",
            )
        )
    return posts


def split_frontmatter(text: str) -> tuple[dict[str, Any], str]:
    if not text.startswith("---"):
        return {}, text
    match = re.match(r"^---\s*\n(.*?)\n---\s*\n(.*)$", text, flags=re.S)
    if not match:
        raise ValueError("Invalid frontmatter: missing closing ---")
    metadata = yaml.safe_load(match.group(1)) or {}
    if not isinstance(metadata, dict):
        raise ValueError("Invalid frontmatter: expected mapping")
    return metadata, match.group(2)


def required_str(metadata: dict[str, Any], key: str, md_path: Path) -> str:
    value = str(metadata.get(key) or "").strip()
    if not value:
        raise ValueError(f"{md_path} missing required frontmatter field: {key}")
    return value


def parse_date(value: Any, md_path: Path) -> date:
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    if isinstance(value, str):
        return datetime.strptime(value.strip(), "%Y-%m-%d").date()
    raise ValueError(f"{md_path} missing valid date frontmatter field")


def first_tag(metadata: dict[str, Any]) -> str:
    tags = metadata.get("tags")
    if isinstance(tags, list) and tags:
        return str(tags[0])
    return ""


def markdown_to_html(body_md: str) -> str:
    body_md = re.sub(
        r"```mermaid\s*\n(.*?)```",
        lambda match: "\n<div class=\"mermaid\">\n" + match.group(1).strip("\n") + "\n</div>\n",
        body_md,
        flags=re.S,
    )
    body_html = markdown.markdown(
        body_md,
        extensions=["extra", "fenced_code", "tables", "sane_lists"],
        output_format="html5",
    )
    body_html = re.sub(r"(<table>.*?</table>)", r'<div class="table-wrap">\1</div>', body_html, flags=re.S)
    body_html = re.sub(r"<p>(<img [^>]+>)</p>", r"<figure>\1</figure>", body_html)
    return body_html


def write_post_html(post: Post) -> None:
    output = POSTS_DIR / f"{post.slug}.html"
    output.write_text(render_post_template(post), encoding="utf-8")


def render_post_template(post: Post) -> str:
    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{escape(post.title)} | PGH Blog</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://pgh11.github.io/pgh-blog/styles.css">
    {post_style()}
</head>
<body>
    {theme_toggle()}
    <div id="navbar-placeholder"></div>
    <section class="post-header">
        <div class="post-container">
            <a href="https://pgh11.github.io/pgh-blog/blog.html" class="back-btn"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="width: 20px; height: 20px;"><polyline points="15 18 9 12 15 6"></polyline></svg>返回博客列表</a>
            <h1 class="post-title">{escape(post.title)}</h1>
            <div class="post-meta"><span class="post-category">{escape(post.category)}</span><span class="post-date">{post.display_date}</span></div>
            <p class="post-summary">{escape(post.summary)}</p>
        </div>
    </section>
    <article class="post-content">
        <div class="post-container">
            {post.body_html}
        </div>
    </article>
    <div id="footer-placeholder"></div>
    <script type="module">
        import mermaid from "https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs";
        mermaid.initialize({{ startOnLoad: true, theme: "default", securityLevel: "loose" }});
    </script>
    <script src="../components/load-components.js"></script>
    <script src="https://pgh11.github.io/pgh-blog/script.js"></script>
</body>
</html>
"""


def post_style() -> str:
    return """<style>
        .post-header { padding: 160px 24px 60px; background: radial-gradient(circle at 50% 0%, rgba(59, 130, 246, 0.15) 0%, transparent 50%), var(--bg-primary); }
        .post-container { max-width: 880px; margin: 0 auto; }
        .post-title { font-size: 42px; font-weight: 700; line-height: 1.3; margin-bottom: 24px; }
        .post-meta { display: flex; align-items: center; gap: 16px; margin-bottom: 24px; flex-wrap: wrap; }
        .post-category { padding: 6px 16px; background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%); color: white; border-radius: 20px; font-size: 13px; font-weight: 600; }
        .post-date { color: var(--text-tertiary); font-size: 15px; }
        .post-summary { color: var(--text-secondary); font-size: 18px; line-height: 1.8; max-width: 780px; }
        .post-content { padding: 40px 24px 80px; }
        .post-content h1 { font-size: 34px; font-weight: 700; margin: 24px 0 24px; color: var(--text-primary); }
        .post-content h2 { font-size: 28px; font-weight: 600; margin: 42px 0 20px; color: var(--text-primary); }
        .post-content h3 { font-size: 22px; font-weight: 600; margin: 34px 0 16px; color: var(--text-primary); }
        .post-content h4 { font-size: 18px; font-weight: 600; margin: 28px 0 14px; color: var(--text-primary); }
        .post-content p { color: var(--text-secondary); line-height: 1.85; margin-bottom: 20px; font-size: 17px; }
        .post-content ul, .post-content ol { color: var(--text-secondary); line-height: 1.8; margin-bottom: 22px; padding-left: 24px; }
        .post-content li { margin-bottom: 10px; font-size: 17px; }
        .post-content a { color: #3b82f6; text-decoration: none; }
        .post-content a:hover { text-decoration: underline; }
        .post-content code { background: var(--bg-secondary); padding: 2px 8px; border-radius: 6px; font-family: 'JetBrains Mono', monospace; font-size: 14px; color: #3b82f6; }
        .post-content pre { background: var(--bg-secondary); padding: 20px; border-radius: 12px; overflow-x: auto; margin-bottom: 24px; border: 1px solid var(--border-color); }
        .post-content pre code { background: none; padding: 0; color: var(--text-primary); font-size: 14px; line-height: 1.8; }
        .post-content .mermaid { background: var(--bg-secondary); border: 1px solid var(--border-color); border-radius: 12px; padding: 24px; margin: 28px 0; overflow-x: auto; text-align: center; }
        .post-content .mermaid svg { max-width: 100%; height: auto; }
        .post-content blockquote { border-left: 4px solid #3b82f6; padding-left: 20px; margin: 24px 0; color: var(--text-tertiary); font-style: italic; }
        .post-content figure { margin: 32px 0; }
        .post-content img { width: 100%; border-radius: 12px; border: 1px solid var(--border-color); background: var(--bg-secondary); }
        .table-wrap { overflow-x: auto; margin: 28px 0; border: 1px solid var(--border-color); border-radius: 12px; }
        .post-content table { width: 100%; border-collapse: collapse; min-width: 640px; }
        .post-content th, .post-content td { padding: 12px 14px; border-bottom: 1px solid var(--border-color); text-align: left; color: var(--text-secondary); vertical-align: top; }
        .post-content th { color: var(--text-primary); background: var(--bg-secondary); font-weight: 600; }
        .back-btn { display: inline-flex; align-items: center; gap: 8px; color: #3b82f6; text-decoration: none; font-weight: 500; margin-bottom: 32px; transition: transform 0.3s ease; }
        .back-btn:hover { transform: translateX(-4px); }
        @media (max-width: 768px) { .post-title { font-size: 32px; } .post-container { max-width: 100%; } }
    </style>"""


def theme_toggle() -> str:
    return """<div class="theme-toggle" id="themeToggle">
        <svg class="sun-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="12" cy="12" r="5"></circle>
            <line x1="12" y1="1" x2="12" y2="3"></line>
            <line x1="12" y1="21" x2="12" y2="23"></line>
            <line x1="4.22" y1="4.22" x2="5.64" y2="5.64"></line>
            <line x1="18.36" y1="18.36" x2="19.78" y2="19.78"></line>
            <line x1="1" y1="12" x2="3" y2="12"></line>
            <line x1="21" y1="12" x2="23" y2="12"></line>
            <line x1="4.22" y1="19.78" x2="5.64" y2="18.36"></line>
            <line x1="18.36" y1="5.64" x2="19.78" y2="4.22"></line>
        </svg>
        <svg class="moon-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"></path>
        </svg>
    </div>"""


def update_blog_index(posts: list[Post]) -> None:
    html_text = BLOG_HTML.read_text(encoding="utf-8")
    legacy_cards = extract_blog_cards(html_text)
    generated_hrefs = {post.href for post in posts}
    cards = [render_blog_card(post, index) for index, post in enumerate(posts)]
    cards.extend(card for href, card in legacy_cards if href not in generated_hrefs)
    new_grid = '<div class="blog-grid">\n' + "\n\n".join(cards) + "\n            </div>"
    BLOG_HTML.write_text(replace_blog_grid(html_text, new_grid), encoding="utf-8")


def extract_blog_cards(html_text: str) -> list[tuple[str, str]]:
    cards: list[tuple[str, str]] = []
    for match in re.finditer(r'\s*<article class="blog-card">.*?</article>', html_text, flags=re.S):
        card = normalize_existing_card(match.group(0))
        href_match = re.search(r'<a href="([^"]+)" class="blog-read-more">', card)
        if href_match:
            cards.append((href_match.group(1), "                " + card.replace("\n", "\n                ")))
    return cards


def render_blog_card(post: Post, index: int) -> str:
    start, end = COLORS[index % len(COLORS)]
    return f"""                <article class="blog-card">
                    <div class="blog-image" style="background: linear-gradient(135deg, {start} 0%, {end} 100%);"></div>
                    <div class="blog-content">
                        <div class="blog-meta">
                            <span class="blog-category">{escape(post.category)}</span>
                            <span class="blog-date">{post.display_date}</span>
                        </div>
                        <h3 class="blog-title">{escape(post.title)}</h3>
                        <p class="blog-excerpt">
                            {escape(post.summary)}
                        </p>
                        <a href="{post.href}" class="blog-read-more">阅读全文 →</a>
                    </div>
                </article>"""


def replace_blog_grid(html_text: str, new_grid: str) -> str:
    start = html_text.index('<div class="blog-grid">')
    end_marker = "\n        </div>\n    </section>"
    end = html_text.index(end_marker, start)
    return html_text[:start] + new_grid + html_text[end:]


def update_home_recent_posts(posts: list[Post]) -> None:
    if not INDEX_HTML.exists() or not posts:
        return
    html_text = INDEX_HTML.read_text(encoding="utf-8")
    if '<div class="home-posts">' not in html_text:
        return
    generated_hrefs = {post.href for post in posts}
    cards = [render_home_card(post) for post in posts]
    cards.extend(card for href, card in extract_home_cards(html_text) if href not in generated_hrefs)
    cards = cards[:3]
    new_block = '<div class="home-posts">\n' + "\n".join(cards) + "\n                </div>"
    start = html_text.index('<div class="home-posts">')
    end = html_text.index("\n                </div>", start) + len("\n                </div>")
    INDEX_HTML.write_text(html_text[:start] + new_block + html_text[end:], encoding="utf-8")


def extract_home_cards(html_text: str) -> list[tuple[str, str]]:
    cards: list[tuple[str, str]] = []
    for match in re.finditer(r'\s*<a class="home-post" href="([^"]+)">.*?</a>', html_text, flags=re.S):
        card = normalize_existing_card(match.group(0))
        cards.append((match.group(1), "                    " + card.replace("\n", "\n                    ")))
    return cards


def normalize_existing_card(card: str) -> str:
    lines: list[str] = []
    level = 0
    for raw_line in textwrap.dedent(card).strip().splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if line.startswith("</"):
            level = max(level - 1, 0)
        lines.append("    " * level + line)
        opening = re.match(r"<([a-zA-Z][\w-]*)(\s|>|/)", line)
        if opening:
            tag = opening.group(1)
            closes_on_same_line = f"</{tag}>" in line or line.endswith("/>")
            if not closes_on_same_line and not line.startswith("</"):
                level += 1
    return "\n".join(lines)


def render_home_card(post: Post) -> str:
    return f"""                    <a class="home-post" href="{post.href}">
                        <span>
                            <span class="home-post-meta">
                                <span>{escape(post.category)}</span>
                                <span>{post.compact_date}</span>
                            </span>
                            <h3 class="home-post-title">{escape(post.title)}</h3>
                        </span>
                        <span class="home-post-more">阅读文章</span>
                    </a>"""


def escape(value: str) -> str:
    return html.escape(value, quote=True)


if __name__ == "__main__":
    main()
