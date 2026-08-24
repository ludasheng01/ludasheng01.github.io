# 拾光小站 · 个人博客

一个用 **Markdown 写作** 的轻量级个人博客，由 Python 脚本一键生成静态网页。无需服务器、无需数据库，构建后可以把 `public/` 文件夹免费部署到 GitHub Pages / Vercel / Netlify 等平台（已内置 GitHub Actions 自动部署）。

## 功能特性

- 首页文章列表、文章页（上一篇/下一篇）、**分类**、标签、归档、关于
- **站内搜索**：顶栏搜索框直达 `/search/`，支持标题 / 标签 / 摘要匹配
- **代码语法高亮**：构建时用 Pygments 生成，亮色 / 深色自动适配
- **阅读时间与字数统计**：每篇文章自动显示
- **相关文章推荐**：按标签重合自动推荐
- **SEO 优化**：Open Graph、canonical、sitemap
- **自定义 404 页面**
- **回到顶部按钮**、深色模式、手机响应式
- **Giscus 评论**（已配置）
- **访问统计**（不蒜子：站点总访问 / 访客数 / 文章阅读量，可在 `config.json` 关闭）
- **文章封面图**（frontmatter 里写 `cover:`，自动用于首页缩略图、文章横幅和分享图）
- **RSS 全文输出**（`content:encoded` 全文 + 封面图）

## 快速开始

```bash
# 1. 构建站点（输出到 public/）
python build.py

# 2. 本地预览
python build.py --serve
# 打开 http://127.0.0.1:8000/
```

## 写一篇文章

1. 在 `content/posts/` 下新建一个 `.md` 文件（文件名会成为网址，建议用英文或拼音）。
2. 文件开头用 `---` 写基本信息，正文用 Markdown：

```markdown
---
title: 我的第一篇文章
date: 2026-08-24
category: 教程                        # 分类（每篇一个，可选）
tags: [教程, 随笔]
cover: /assets/images/covers/xxx.svg   # 可选：文章封面图
summary: 一句话摘要，会显示在首页。
draft: false
---

这里是正文。
```

3. 运行 `python build.py` 重新生成，然后 `git push` 自动部署。

## 自定义站点（改配置即可，不用改代码）

打开 `config.json`：

| 字段 | 说明 |
| --- | --- |
| `site.title` | 博客标题 |
| `site.subtitle` | 首页副标题 |
| `site.author` | 作者署名 |
| `site.description` | 站点描述（用于 SEO） |
| `site.url` | 部署后的网址 |
| `site.base` | GitHub Pages 项目站点的子路径（根域名部署留空） |

修改后重新运行 `python build.py`。

## 评论（Giscus，已配置好）

评论已经接入 [Giscus](https://giscus.app)（基于 GitHub Discussions，免费无广告），`config.json` 里已填好仓库和分类 ID。

**还差一步（一次性）：** 安装 giscus 应用到仓库 → 打开 [github.com/apps/giscus](https://github.com/apps/giscus)，点 **Install**，选择 `ludasheng01/ludasheng01.github.io` 即可。安装后文章页底部自动出现评论区。

想换评论分类或仓库时，修改 `config.json` 的 `comments` 段：

```json
"comments": {
  "enabled": true,
  "repo": "ludasheng01/ludasheng01.github.io",
  "repo_id": "R_kgDOUBkB6w",
  "category": "Announcements",
  "category_id": "DIC_kwDOUBkB684DEBCf",
  "mapping": "pathname",
  "lang": "zh-CN"
}
```

## 绑定自定义域名（可选）

1. 在域名服务商处把域名解析到 GitHub Pages：添加 CNAME 记录 `你的域名` → `ludasheng01.github.io`。
2. 到仓库 **Settings → Pages → Custom domain** 填上你的域名并保存（会自动生成 CNAME 文件）。
3. 把 `config.json` 的 `site.url` 改成你的域名，重新部署。

## 部署到 GitHub Pages（已完成）

仓库已配置 **Settings → Pages → Source: GitHub Actions**，推送 `master` 分支即自动构建上线（`.github/workflows/deploy.yml`），线上地址：`https://ludasheng01.github.io/`。

## 目录结构

```
├── build.py              # 构建脚本
├── config.json           # 站点信息与评论配置
├── content/
│   ├── about.md          # 关于页面
│   └── posts/            # 文章，每篇一个 .md 文件
├── assets/
│   ├── css/style.css     # 主题样式
│   └── images/           # 头像、favicon、配图
├── templates/            # 页面模板
├── .github/workflows/    # GitHub Actions 自动部署
└── public/               # 构建产物（部署这个文件夹）
```

## 写作小技巧

- `category` 写文章分类（每篇一个），自动生成分类页；`tags` 用逗号分隔，自动生成标签页。
- 想先存草稿？加 `draft: true`，构建时自动跳过。
- 正文写 `[TOC]` 可自动生成文章目录。
- 支持代码块、表格、引用、图片等常见 Markdown 语法。
