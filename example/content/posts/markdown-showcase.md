---
title: Markdown 语法一览
date: 2026-10-24
tags: [markdown, 教程]
description: mksite 内置 Markdown 引擎支持的全部语法示例。
---

# Markdown 语法一览

这篇文章覆盖 mksite 内置引擎支持的所有语法，可以直接当写作模板用。

## 行内元素

**粗体**、*斜体*、`行内代码`、~~删除线~~，以及[链接](https://www.python.org)
和图片 `![alt](src)`。HTML 会被自动转义：`<script>` 永远不会被执行。

## 引用

> 零依赖意味着：一个 Python 解释器 + 一个包，就是全部运行环境。
>
> > 嵌套引用也没问题。

## 列表

无序列表支持嵌套：

- 静态站点生成
  - Markdown 渲染
  - 模板变量
- 开发服务器
- RSS / sitemap

有序列表（起始编号不是 1 也可以）：

3. 第三名
4. 第四名

## 代码块

```python
from mksite.markdown import md_to_html

html = md_to_html("# Hello, **mksite**!")
print(html)  # <h1 id="hello-mksite">Hello, <strong>mksite</strong>!</h1>
```

表格支持按列对齐：

| 命令 | 作用 | 备注 |
| :-- | :---: | --: |
| `mksite init` | 初始化站点 | 必备 |
| `mksite build` | 构建静态文件 | 必备 |
| `mksite serve` | 本地预览 | 可选 |
| `mksite new` | 新建文章 | 可选 |

---

水平线之上是分割线语法 `---`。标题会自动生成锚点 id，
比如 [这个链接](#代码块) 可以跳转到「代码块」一节。
