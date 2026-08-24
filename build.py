#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""轻量级静态博客生成器。

用法:
    python build.py            构建站点到 public/
    python build.py --drafts   连草稿一起构建
    python build.py --serve    构建并启动本地预览服务器
"""
import argparse
import html
import json
import re
import shutil
import sys
from datetime import datetime
from pathlib import Path

import markdown

ROOT = Path(__file__).resolve().parent
CONTENT_DIR = ROOT / "content"
POSTS_DIR = CONTENT_DIR / "posts"
ASSETS_DIR = ROOT / "assets"
TEMPLATES_DIR = ROOT / "templates"
PUBLIC_DIR = ROOT / "public"

# 站点信息从 config.json 读取（无需改代码）
DEFAULTS = {
    "site": {
        "title": "我的博客",
        "subtitle": "记录思考，分享成长",
        "author": "博主",
        "description": "一个用 Markdown 写作的轻量个人博客。",
        "url": "https://example.com",
        "base": "",
        "language": "zh-CN",
        "posts_per_page": 20,
    },
    "comments": {
        "enabled": False,
        "provider": "giscus",
        "repo": "",
        "repo_id": "",
        "category": "Announcements",
        "category_id": "",
        "mapping": "pathname",
        "lang": "zh-CN",
    },
}


def load_config():
    cfg_path = ROOT / "config.json"
    cfg = json.loads(json.dumps(DEFAULTS))
    if cfg_path.exists():
        user_cfg = json.loads(cfg_path.read_text(encoding="utf-8"))
        for section in ("site", "comments"):
            if section in user_cfg and isinstance(user_cfg[section], dict):
                cfg[section].update(user_cfg[section])
    return cfg


CONFIG = load_config()
SITE = CONFIG["site"]
COMMENTS = CONFIG["comments"]

MD_EXTENSIONS = ["fenced_code", "tables", "toc", "attr_list", "sane_lists", "def_list", "codehilite"]


def render_markdown(body):
    md = markdown.Markdown(
        extensions=MD_EXTENSIONS,
        extension_configs={"codehilite": {"guess_lang": False, "css_class": "highlight", "noclasses": False}},
        output_format="html5",
    )
    content_html = md.convert(body)
    toc = getattr(md, "toc", "")
    # 支持在正文里写 [TOC] 生成目录
    content_html = content_html.replace("<p>[TOC]</p>", toc)
    return content_html, toc


def reading_stats(body):
    """粗略统计正文阅读时长与字数。"""
    body = re.sub(r"```.*?```", "", body, flags=re.S)
    body = re.sub(r"[#>*_`\[\]()!\-]", "", body)
    cjk = len(re.findall(r"[\u4e00-\u9fff]", body))
    words = len(re.findall(r"[A-Za-z0-9]+", body))
    total = cjk + words
    minutes = max(1, round(total / 400))
    return minutes, total


def parse_frontmatter(text):
    """解析 --- 包裹的简单 frontmatter，返回 (meta, body)。"""
    if not text.startswith("---"):
        return {}, text
    end = text.find("\n---", 3)
    if end == -1:
        return {}, text
    fm = text[3:end].strip()
    body = text[end + 4:].lstrip("\n")
    meta = {}
    for line in fm.splitlines():
        line = line.strip()
        if not line or line.startswith("#") or ":" not in line:
            continue
        key, _, value = line.partition(":")
        key = key.strip().lower()
        value = value.strip().strip('"').strip("'")
        if not value:
            continue
        if key == "tags":
            value = value.strip()
            if value.startswith("[") and value.endswith("]"):
                value = value[1:-1]
            meta[key] = [t.strip() for t in re.split(r"[，,]", value) if t.strip()]
        elif key == "draft":
            meta[key] = value.lower() in ("true", "yes", "1")
        else:
            meta[key] = value
    return meta, body


def parse_date(value):
    value = value.strip()
    for fmt in ("%Y-%m-%d %H:%M", "%Y-%m-%d", "%Y/%m/%d"):
        try:
            return datetime.strptime(value, fmt)
        except ValueError:
            continue
    return datetime.now()


def slugify(name):
    stem = Path(name).stem
    slug = re.sub(r"[^a-zA-Z0-9\u4e00-\u9fff]+", "-", stem).strip("-")
    return slug or "post"


def read_post(path):
    text = path.read_text(encoding="utf-8")
    meta, body = parse_frontmatter(text)
    content_html, toc = render_markdown(body)
    date = parse_date(meta.get("date", "")) if meta.get("date") else datetime.now()
    minutes, words = reading_stats(body)
    return {
        "slug": slugify(path.name),
        "reading_minutes": minutes,
        "word_count": words,
        "title": meta.get("title", Path(path).stem),
        "date": date,
        "tags": meta.get("tags", []),
        "draft": bool(meta.get("draft", False)),
        "summary": meta.get("summary", ""),
        "content_html": content_html,
        "toc": toc,
        "source": path.name,
    }


def load_posts(include_drafts=False):
    posts = []
    if POSTS_DIR.exists():
        for path in sorted(POSTS_DIR.glob("*.md")):
            post = read_post(path)
            if post["draft"] and not include_drafts:
                continue
            posts.append(post)
    posts.sort(key=lambda p: p["date"], reverse=True)
    return posts


def load_page(name):
    path = CONTENT_DIR / name
    if not path.exists():
        return None
    meta, body = parse_frontmatter(path.read_text(encoding="utf-8"))
    content_html, _ = render_markdown(body)
    return {
        "title": meta.get("title", name),
        "content_html": content_html,
    }


def render_template(name, **kwargs):
    path = TEMPLATES_DIR / name
    text = path.read_text(encoding="utf-8")
    for key, value in kwargs.items():
        text = text.replace("{{" + key + "}}", str(value))
    return text


def format_date(dt, fmt="%Y 年 %m 月 %d 日"):
    return dt.strftime(fmt)


def giscus_html():
    """生成 Giscus 评论脚本；未配置时返回空字符串。"""
    if not COMMENTS.get("enabled") or not COMMENTS.get("repo"):
        return ""
    return f'''
<section class="post-comments">
  <h2>评论</h2>
  <script src="https://giscus.app/client.js"
    data-repo="{html.escape(COMMENTS['repo'])}"
    data-repo-id="{html.escape(COMMENTS.get('repo_id') or '')}"
    data-category="{html.escape(COMMENTS.get('category') or 'Announcements')}"
    data-category-id="{html.escape(COMMENTS.get('category_id') or '')}"
    data-mapping="{html.escape(COMMENTS.get('mapping') or 'pathname')}"
    data-strict="0"
    data-reactions-enabled="1"
    data-emit-metadata="0"
    data-input-position="bottom"
    data-theme="preferred_color_scheme"
    data-lang="{html.escape(COMMENTS.get('lang') or 'zh-CN')}"
    crossorigin="anonymous"
    async>
  </script>
</section>'''


def write_highlight_css():
    """生成代码高亮样式（亮色 + 深色两套，随系统切换）。"""
    try:
        from pygments.formatters import HtmlFormatter
        light = HtmlFormatter(style="friendly").get_style_defs(".highlight")
        dark = HtmlFormatter(style="monokai").get_style_defs(".highlight")
        css = light + "\n@media (prefers-color-scheme: dark) {\n" + dark + "\n}\n"
        out = PUBLIC_DIR / "assets" / "css" / "highlight.css"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(css, encoding="utf-8")
    except ImportError:
        pass


def build():
    if PUBLIC_DIR.exists():
        shutil.rmtree(PUBLIC_DIR)
    PUBLIC_DIR.mkdir(parents=True)

    # 复制静态资源
    if ASSETS_DIR.exists():
        shutil.copytree(ASSETS_DIR, PUBLIC_DIR / "assets")
        # 顺带把 favicon 放到根目录
        favicon = PUBLIC_DIR / "assets" / "images" / "favicon.svg"
        if favicon.exists():
            shutil.copy(favicon, PUBLIC_DIR / "favicon.svg")
    write_highlight_css()

    posts = load_posts(include_drafts=args.drafts)
    pages = {"about": load_page("about.md")}

    base = SITE["base"].rstrip("/")
    year = datetime.now().year

    def url(path):
        return (base + "/" + path.lstrip("/")).replace("//", "/")

    # ---------- 首页 ----------
    def post_item(post, show_summary=True):
        tags_html = "".join(
            f'<a class="tag" href="{url("tags/" + slugify(tag) + "/")}">#{tag}</a>'
            for tag in post["tags"]
        )
        summary = post["summary"] or strip_html(post["content_html"])[:140]
        return (
            f'<article class="post-item">'
            f'<h2 class="post-item-title"><a href="{url("posts/" + post["slug"] + "/")}">{html.escape(post["title"])}</a></h2>'
            f'<div class="post-meta"><time datetime="{post["date"].isoformat()}">{format_date(post["date"])}</time> {tags_html}</div>'
            f'<p class="post-item-summary">{html.escape(summary)}</p>'
            f"</article>"
        )

    index_items = "\n".join(post_item(p) for p in posts[: SITE["posts_per_page"]])
    index_content = render_template(
        "index.html",
        SUBTITLE=SITE["subtitle"],
        POSTS=index_items,
        POST_COUNT=len(posts),
    )

    # ---------- 文章页 ----------
    for post in posts:
        tags_html = "".join(
            f'<a class="tag" href="{url("tags/" + slugify(tag) + "/")}">#{tag}</a>'
            for tag in post["tags"]
        )
        # 上一篇 / 下一篇
        idx = posts.index(post)
        prev_post = posts[idx + 1] if idx + 1 < len(posts) else None
        next_post = posts[idx - 1] if idx - 1 >= 0 else None
        prev_html = (
            f'<a href="{url("posts/" + prev_post["slug"] + "/")}">← {html.escape(prev_post["title"])}</a>'
            if prev_post else "<span></span>"
        )
        next_html = (
            f'<a href="{url("posts/" + next_post["slug"] + "/")}">{html.escape(next_post["title"])} →</a>'
            if next_post else "<span></span>"
        )
        # 相关文章（按标签重合推荐）
        related = []
        for other in posts:
            if other["slug"] == post["slug"]:
                continue
            if set(other["tags"]) & set(post["tags"]):
                related.append(other)
        related = related[:3]
        related_html = ""
        if related:
            related_html = (
                '<section class="related-posts"><h2>相关文章</h2><ul>'
                + "".join(
                    f'<li><a href="{url("posts/" + p["slug"] + "/")}">{html.escape(p["title"])}</a></li>'
                    for p in related
                )
                + "</ul></section>"
            )
        content = render_template(
            "post.html",
            TITLE=html.escape(post["title"]),
            DATE=format_date(post["date"]),
            DATE_ISO=post["date"].isoformat(),
            TAGS=tags_html,
            READING_TIME=f'<span>约 {post["reading_minutes"]} 分钟 · {post["word_count"]} 字</span>',
            CONTENT=post["content_html"],
            TOC=post["toc"],
            COMMENTS=giscus_html(),
            RELATED=related_html,
            PREV=prev_html,
            NEXT=next_html,
        )
        out = PUBLIC_DIR / "posts" / post["slug"]
        out.mkdir(parents=True, exist_ok=True)
        (out / "index.html").write_text(
            wrap_layout(content, html.escape(post["title"]), SITE["description"], "posts",
                        path=f"/posts/{post['slug']}/", og_type="article"),
            encoding="utf-8",
        )

    # ---------- 标签 ----------
    tag_posts = {}
    for post in posts:
        for tag in post["tags"]:
            tag_posts.setdefault(tag, []).append(post)
    tag_list = "".join(
        f'<a class="tag tag--big" href="{url("tags/" + slugify(tag) + "/")}">#{tag} <span class="tag-count">{len(items)}</span></a>'
        for tag, items in sorted(tag_posts.items(), key=lambda kv: -len(kv[1]))
    )
    tags_index = render_template("tags.html", TAG_LIST=tag_list)
    write_page("tags", tags_index, "标签", SITE["description"])

    for tag, items in tag_posts.items():
        tag_items = "\n".join(
            f'<li class="archive-item"><span class="archive-date">{format_date(p["date"], "%Y-%m-%d")}</span> '
            f'<a href="{url("posts/" + p["slug"] + "/")}">{html.escape(p["title"])}</a></li>'
            for p in items
        )
        tag_slug = slugify(tag)
        content = render_template("tag.html", TAG=html.escape(tag), POSTS=tag_items)
        out = PUBLIC_DIR / "tags" / tag_slug
        out.mkdir(parents=True, exist_ok=True)
        (out / "index.html").write_text(
            wrap_layout(content, f"标签：{tag}", SITE["description"], "tags", path=f"/tags/{tag_slug}/"),
            encoding="utf-8",
        )

    # ---------- 归档 ----------
    by_year = {}
    for post in posts:
        by_year.setdefault(post["date"].year, []).append(post)
    archive_html = []
    for year_key in sorted(by_year, reverse=True):
        items = "".join(
            f'<li class="archive-item"><span class="archive-date">{format_date(p["date"], "%Y-%m-%d")}</span> '
            f'<a href="{url("posts/" + p["slug"] + "/")}">{html.escape(p["title"])}</a>'
            f'<span class="archive-tags">{"".join(f"#{t} " for t in p["tags"])}</span></li>'
            for p in by_year[year_key]
        )
        archive_html.append(f'<section class="archive-year"><h2>{year_key}</h2><ul class="archive-list">{items}</ul></section>')
    archive_content = render_template("archive.html", YEARS="\n".join(archive_html))
    write_page("archive", archive_content, "归档", SITE["description"])

    # ---------- 关于 ----------
    if pages["about"]:
        about = pages["about"]
        about_content = render_template("about.html", CONTENT=about["content_html"], BASE=SITE["base"])
        write_page("about", about_content, about["title"], SITE["description"])

    # ---------- 搜索 ----------
    search_index = [
        {
            "title": p["title"],
            "url": f"{base}/posts/{p['slug']}/",
            "date": p["date"].strftime("%Y-%m-%d"),
            "tags": p["tags"],
            "summary": (p["summary"] or strip_html(p["content_html"]))[:200],
        }
        for p in posts
    ]
    (PUBLIC_DIR / "search.json").write_text(json.dumps(search_index, ensure_ascii=False), encoding="utf-8")
    search_content = render_template("search.html", BASE=SITE["base"])
    write_page("search", search_content, "搜索", "站内搜索")

    # ---------- 404 ----------
    notfound = render_template("404.html", BASE=SITE["base"])
    (PUBLIC_DIR / "404.html").write_text(
        wrap_layout(notfound, "页面未找到", "你访问的页面不存在", "404", path="/404.html"),
        encoding="utf-8",
    )

    # ---------- 首页 & RSS & sitemap ----------
    (PUBLIC_DIR / "index.html").write_text(
        wrap_layout(index_content, SITE["title"], SITE["description"], "home", path="/"),
        encoding="utf-8",
    )
    write_rss(posts, base)
    write_sitemap(posts, list(tag_posts), base)

    print(f"[OK] 构建完成：{len(posts)} 篇文章 -> {PUBLIC_DIR}")


def strip_html(text):
    text = re.sub(r"<[^>]+>", "", text)
    return re.sub(r"\s+", " ", text).strip()


def wrap_layout(content, page_title, description, active, path="/", og_type="website"):
    full_title = page_title if page_title == SITE["title"] else f"{page_title} · {SITE['title']}"
    base = SITE["base"].rstrip("/")
    page_url = SITE["url"] + base + path
    og_image = SITE["url"] + base + "/assets/images/avatar.svg"
    return render_template(
        "base.html",
        PAGE_TITLE=full_title,
        DESCRIPTION=html.escape(description),
        PAGE_URL=html.escape(page_url),
        OG_IMAGE=html.escape(og_image),
        OG_TYPE=og_type,
        LANG=SITE["language"],
        BASE=SITE["base"],
        SITE_TITLE=html.escape(SITE["title"]),
        AUTHOR=html.escape(SITE["author"]),
        YEAR=datetime.now().year,
        NAV_HOME='class="active"' if active == "home" else "",
        NAV_ARCHIVE='class="active"' if active == "archive" else "",
        NAV_TAGS='class="active"' if active == "tags" else "",
        NAV_ABOUT='class="active"' if active == "about" else "",
        PAGE_CONTENT=content,
    )


def write_page(slug, content, title, description):
    out = PUBLIC_DIR / slug
    out.mkdir(parents=True, exist_ok=True)
    (out / "index.html").write_text(
        wrap_layout(content, title, description, slug, path=f"/{slug}/"),
        encoding="utf-8",
    )


def write_rss(posts, base):
    items = []
    for post in posts[:10]:
        items.append(
            "<item>"
            f"<title>{html.escape(post['title'])}</title>"
            f"<link>{SITE['url']}{base}/posts/{post['slug']}/</link>"
            f"<guid>{SITE['url']}{base}/posts/{post['slug']}/</guid>"
            f"<pubDate>{post['date'].strftime('%a, %d %b %Y %H:%M:%S +0800')}</pubDate>"
            f"<description>{html.escape(strip_html(post['content_html'])[:500])}</description>"
            "</item>"
        )
    rss = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">\n'
        "<channel>\n"
        f"<title>{html.escape(SITE['title'])}</title>\n"
        f"<link>{SITE['url']}{base}/</link>\n"
        f"<description>{html.escape(SITE['description'])}</description>\n"
        "<language>zh-cn</language>\n"
        + "\n".join(items)
        + "\n</channel>\n</rss>\n"
    )
    (PUBLIC_DIR / "rss.xml").write_text(rss, encoding="utf-8")


def write_sitemap(posts, tags, base):
    urls = [f"{SITE['url']}{base}/", f"{SITE['url']}{base}/archive/", f"{SITE['url']}{base}/tags/"]
    urls += [f"{SITE['url']}{base}/posts/{p['slug']}/" for p in posts]
    urls += [f"{SITE['url']}{base}/tags/{t}/" for t in tags]
    xml = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    xml += "".join(f"<url><loc>{u}</loc></url>\n" for u in urls)
    xml += "</urlset>\n"
    (PUBLIC_DIR / "sitemap.xml").write_text(xml, encoding="utf-8")


def serve():
    import http.server

    base = SITE["base"].rstrip("/")

    class Handler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=str(PUBLIC_DIR), **kwargs)

        def translate_path(self, path):
            # 本地预览时支持 /blog/... 这种子路径前缀，和线上保持一致
            if base and path == base:
                path = "/"
            elif base and path.startswith(base + "/"):
                path = path[len(base):]
            return super().translate_path(path)

    port = 8000
    with http.server.ThreadingHTTPServer(("127.0.0.1", port), Handler) as httpd:
        print(f"预览地址: http://127.0.0.1:{port}{base}/  (Ctrl+C 停止)")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n已停止。")


parser = argparse.ArgumentParser(description="构建静态博客")
parser.add_argument("--drafts", action="store_true", help="把草稿也构建进去")
parser.add_argument("--serve", action="store_true", help="构建后启动本地预览服务器")
args = parser.parse_args()

build()
if args.serve:
    serve()
