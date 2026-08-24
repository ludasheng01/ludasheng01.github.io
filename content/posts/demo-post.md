---
title: 发表文章与插入图片的完整示例
date: 2026-08-24
category: 教程
tags: [教程, 博客, Markdown]
cover: /assets/images/covers/cover-demo.svg
summary: 这篇示范文章手把手展示如何发表文章、插入本地图片和网络图片、设置封面图。
---

这篇是一篇**示范文章**，用来展示发表文章和插入图片的完整流程。

## 一、本地图片

把图片文件放进 `assets/images/` 文件夹，然后在正文里用下面的语法引用：

```markdown
![写作到发布流程](/assets/images/demo-illustration.svg)
```

效果如下：

![写作到发布流程](/assets/images/demo-illustration.svg)

## 二、网络图片

不保存文件，直接引用图片链接（比如图床、云存储或任意网址）：

```markdown
![网络示例图片](https://picsum.photos/seed/shi-guang/800/450)
```

效果如下（若网络图片加载失败，会显示说明文字）：

![网络示例图片](https://picsum.photos/seed/shi-guang/800/450)

## 三、封面图

在文章开头的 frontmatter 里写一行 `cover:`，就会自动显示在**首页缩略图**、**文章顶部横幅**和**分享卡片**上：

```markdown
---
title: 我的文章
cover: /assets/images/covers/cover-demo.svg
---
```

本文顶部那张横幅就是封面图的效果。

## 四、其他常用语法一览

**加粗文字**、*斜体文字*、`行内代码`。

- 无序列表项
- 另一个列表项

1. 有序列表项
2. 第二个有序列表项

> 这是一段引用文字，用来强调重点。

| 功能 | 语法 |
| --- | --- |
| 标题 | `# 一级标题` |
| 图片 | `![说明](图片地址)` |
| 链接 | `[文字](网址)` |

```python
def hello():
    print("代码块会自动高亮")
```

## 总结

- **发表**：把 `.md` 文件放进 `content/posts/`，提交推送即可自动上线
- **本地图片**：放进 `assets/images/`，用 `/assets/images/文件名` 引用
- **网络图片**：直接用完整链接
- **封面图**：frontmatter 里的 `cover:` 字段

快去试试写你的第一篇正式文章吧！
