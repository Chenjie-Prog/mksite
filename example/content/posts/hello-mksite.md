---
title: 为什么写一个零依赖的静态站点生成器
date: 2026-10-20
tags: [python, mksite]
description: 造轮子的理由，以及 mksite 的设计取舍。
---

# 为什么写一个零依赖的静态站点生成器

市面上并不缺静态站点生成器：Hugo 快，Astro 现代，Jekyll 生态大。
那为什么还要写一个？

## 依赖是成本

主流工具的依赖树动辄上百个包。对于个人博客这种"写 Markdown、出 HTML"
的需求，这些依赖里 99% 的代码永远不会被执行，但你要为它们付出：

- 安装时间与磁盘空间
- 升级时的破坏性变更
- 安全审计面

mksite 的依赖清单是**零**。只要有 Python 3.9+，它就能跑。

## 小到能被完整理解

核心源码不到两千行：

| 模块 | 职责 | 大约行数 |
| :-- | :-- | --: |
| `markdown.py` | Markdown → HTML 引擎 | ~250 |
| `frontmatter.py` | `key: value` 元数据解析 | ~60 |
| `templates.py` | `{{ 变量 }}` 模板渲染 | ~20 |
| `build.py` | 构建管线、RSS、sitemap | ~250 |
| `server.py` | 开发服务器与文件监听 | ~80 |

每一行都在你的阅读范围之内。想改行为？直接改，不需要读文档。

## 设计取舍

1. **不做插件系统。** 需要新功能时，复制代码改一版比学一套 API 更快。
2. **不追求 CommonMark 100% 兼容。** 覆盖写作中 99% 的语法，
   转义所有 HTML 输入，剩下交给标准。
3. **主题就是一个 HTML 文件。** `{{ 变量 }}` 占位符，五分钟上手。

## 试一试

```bash
git clone https://github.com/USER/mksite.git
cd mksite
python -m mksite serve -s example -p 8000
```

打开 <http://127.0.0.1:8000>，修改 `example/content/` 下任意 Markdown 文件，
保存后刷新浏览器即可看到效果。
