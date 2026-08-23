# 拾光小站 · 个人博客

一个用 **Markdown 写作** 的轻量级个人博客，由 Python 脚本一键生成静态网页。无需服务器、无需数据库，构建后可以把 `public/` 文件夹免费部署到 GitHub Pages / Vercel / Netlify 等平台（已内置 GitHub Actions 自动部署）。

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
tags: [教程, 随笔]
summary: 一句话摘要，会显示在首页。
draft: false
---

这里是正文。
```

3. 运行 `python build.py` 重新生成，刷新浏览器即可看到。

## 自定义站点（改配置即可，不用改代码）

打开 `config.json`：

| 字段 | 说明 |
| --- | --- |
| `site.title` | 博客标题 |
| `site.subtitle` | 首页副标题 |
| `site.author` | 作者署名 |
| `site.description` | 站点描述（用于 SEO） |
| `site.url` | 部署后的网址 |
| `site.base` | 部署到 GitHub Pages 项目站点（`用户名.github.io/仓库名`）时填 `"/仓库名"` |

修改后重新运行 `python build.py`。

## 开启评论（Giscus，基于 GitHub Discussions，免费无广告）

1. 把博客推到 GitHub 仓库，并在仓库 Settings 里开启 **Discussions**。
2. 安装 [giscus app](https://github.com/apps/giscus) 到该仓库。
3. 到 [giscus.app](https://giscus.app) 按提示填写仓库名，生成 `data-repo-id` 和 `data-category-id`。
4. 把结果填进 `config.json` 的 `comments` 段，并把 `enabled` 改为 `true`：

```json
"comments": {
  "enabled": true,
  "repo": "你的用户名/仓库名",
  "repo_id": "R_kgDO...",
  "category": "Announcements",
  "category_id": "DIC_kwDO...",
  "mapping": "pathname",
  "lang": "zh-CN"
}
```

5. 重新构建并部署，文章页底部就会出现评论区。

## 部署到 GitHub Pages（自动）

1. 在 GitHub 上新建仓库，把本目录推送上去（`main` 分支）。
2. 进入仓库 **Settings → Pages**，把 Source 选为 **GitHub Actions**。
3. 推送会自动触发 `.github/workflows/deploy.yml`，几分钟后即可访问 `https://你的用户名.github.io/仓库名/`。
4. 上线后记得把 `config.json` 里的 `url` 改成真实网址；如果用自定义域名，在 Pages 设置里绑定即可。

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

- `tags` 用逗号或空格分隔，自动生成标签页。
- 想先存草稿？加 `draft: true`，构建时自动跳过。
- 正文写 `[TOC]` 可自动生成文章目录。
- 支持代码块、表格、引用、图片等常见 Markdown 语法。
