---
title: 如何用 Markdown 写文章
date: 2026-08-24
tags: [教程, Markdown]
summary: 这个博客的写作方式很简单：新建一个 Markdown 文件，填上标题和标签，构建一下就能发布。
---

这个博客采用"文件即文章"的方式写作：每篇文章就是一个 Markdown 文件，放在 `content/posts/` 目录下。

## 一篇文章长什么样

在文件开头用 `---` 写基本信息（这叫 frontmatter）：

```markdown
---
title: 我的第一篇文章
date: 2026-08-24
tags: [教程, 随笔]
summary: 一句话摘要，会显示在首页。
---

这里是正文，用 Markdown 写就行。
```

## 发布流程

1. 新建文件：`content/posts/my-post.md`
2. 写正文，支持标题、列表、代码、表格、引用等语法
3. 在项目根目录运行：

```bash
python build.py
```

4. 本地预览：

```bash
python build.py --serve
# 然后打开 http://127.0.0.1:8000/
```

## 小技巧

- `date` 支持 `2026-08-24` 或带时间的格式
- `tags` 用逗号或空格分隔，会自动生成标签页
- 想写草稿时加一行 `draft: true`，构建时会自动跳过
- 正文里写 `[TOC]` 可以自动生成文章目录

一切从第一篇开始。
