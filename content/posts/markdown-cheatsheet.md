---
title: Markdown 语法速查表
date: 2026-08-24
category: 教程
tags: [Markdown, 教程]
cover: /assets/images/covers/cover-demo.svg
summary: 一张随时可查的 Markdown 常用语法速查表，写作时遇到不记得的语法来这里找。
---

这是一张**随时可查**的 Markdown 速查表。每个功能都给出"语法"和"效果"，照着写就行。

## 标题

用 `#` 的个数表示级别，最多 6 级：

```markdown
# 一级标题
## 二级标题
### 三级标题
```

## 文字样式

| 效果 | 语法 |
| --- | --- |
| **加粗** | `**加粗**` |
| *斜体* | `*斜体*` |
| `行内代码` | `` `行内代码` `` |

## 列表

```markdown
- 无序列表项
- 无序列表项

1. 有序列表项
2. 有序列表项
```

## 链接与图片

```markdown
[链接文字](https://example.com)

![图片说明](/assets/images/你的图片.jpg)
```

## 引用

```markdown
> 这是一段引用文字。
```

## 代码块

用三个反引号包裹，后面可以写语言名（会自动高亮）：

````markdown
```python
print("你好")
```
````

## 表格

```markdown
| 表头一 | 表头二 |
| --- | --- |
| 内容 | 内容 |
```

## 分割线

```markdown
---
```

## 其他小技巧

- 文章里写 `[TOC]` 可以自动生成目录
- 想写草稿时，在文章开头加 `draft: true`，构建时自动跳过
- 文章的分类、标签、封面图写在文件开头的 `---` 里（frontmatter）：

```markdown
---
title: 文章标题
category: 教程
tags: [Markdown, 教程]
cover: /assets/images/covers/xxx.jpg
summary: 一句话摘要
---
```

## 记不住怎么办？

- 随时打开本文查询
- 仓库里的 `content/文章模板.md` 也是现成范例
- 问 AI（比如我）："这句话用 Markdown 怎么写？"

写多了自然就熟了，祝写作愉快！
