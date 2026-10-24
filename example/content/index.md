---
title: 首页
description: 一个用 mksite 搭建的极简博客示例 —— 零依赖的纯 Python 静态站点生成器。
---

# 你好，这里是 mksite 示例博客

这个站点由 **mksite** 生成：整个工具只用 Python 标准库实现，没有
`pip install`，没有 node_modules，把一个包拷进项目就能用。

## 特性

- 零依赖 —— 纯 Python 标准库，支持 Python 3.9+
- 内置 Markdown 引擎（标题、表格、代码块、引用、嵌套列表……）
- 自动生成 RSS 订阅与 sitemap
- 开发服务器带文件监听，保存即重建
- 单个页面模板 + `{{ 变量 }}` 占位符，主题就是一个 HTML 文件

## 快速开始

```bash
pip install git+https://github.com/USER/mksite.git

mksite init myblog     # 初始化站点
mksite serve -s myblog # 本地预览 http://127.0.0.1:8000
mksite build -s myblog # 构建到 myblog/public/
```

## 文章

- [Markdown 语法一览](posts/markdown-showcase.html) —— 引擎支持的所有语法
- [为什么写一个零依赖的静态站点生成器](posts/hello-mksite.html)

> 提示：这个目录（`example/`）本身就是一份可运行的站点源码，
> 仓库里的 `docs/` 是它构建出的成品，可以直接用 GitHub Pages 部署。
