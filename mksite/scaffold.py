"""Files written by ``mksite init`` — kept as string constants so the whole
tool ships as one plain Python package without data files."""

SITE_JSON = """\
{
  "name": "我的站点",
  "language": "zh-CN",
  "base_url": "",
  "author": ""
}
"""

PAGE_TEMPLATE = """\
<!DOCTYPE html>
<html lang="{{ language }}">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{{ title }} · {{ name }}</title>
  <meta name="description" content="{{ description }}">
  <meta name="generator" content="mksite">
  <link rel="stylesheet" href="{{ root }}/style.css">
</head>
<body>
  <header>
    <a class="site-title" href="{{ root }}/">{{ name }}</a>
    <nav>
      <a href="{{ root }}/">首页</a>
      <a href="{{ root }}/about.html">关于</a>
    </nav>
  </header>
  <main>
{{ content }}
  </main>
  <footer>
    <p>由 <a href="https://github.com/mksite">mksite</a> 生成 ·
       <a href="{{ root }}/feed.xml">RSS 订阅</a></p>
  </footer>
</body>
</html>
"""

STYLE_CSS = """\
:root {
  --bg: #ffffff;
  --fg: #1f2328;
  --muted: #59636e;
  --accent: #0969da;
  --border: #d8dee4;
  --soft-bg: #f6f8fa;
  --code-bg: #f6f8fa;
}

@media (prefers-color-scheme: dark) {
  :root {
    --bg: #0d1117;
    --fg: #e6edf3;
    --muted: #8b949e;
    --accent: #4493f8;
    --border: #30363d;
    --soft-bg: #161b22;
    --code-bg: #161b22;
  }
}

* { box-sizing: border-box; }

body {
  margin: 0 auto;
  padding: 2.5rem 1.25rem 3rem;
  max-width: 46rem;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Noto Sans",
    "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", sans-serif;
  font-size: 1rem;
  line-height: 1.75;
  color: var(--fg);
  background: var(--bg);
}

header {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  margin-bottom: 2.5rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid var(--border);
}

.site-title {
  font-size: 1.25rem;
  font-weight: 700;
  color: var(--fg);
  text-decoration: none;
}

nav a {
  margin-left: 1.1rem;
  color: var(--muted);
  text-decoration: none;
}

nav a:hover { color: var(--accent); }

a { color: var(--accent); }

h1, h2, h3, h4, h5, h6 {
  line-height: 1.3;
  margin: 2.2rem 0 0.8rem;
  font-weight: 700;
}

h1 { font-size: 1.9rem; margin-top: 0; }
h2 { font-size: 1.45rem; border-bottom: 1px solid var(--border); padding-bottom: 0.3rem; }
h3 { font-size: 1.2rem; }

p { margin: 0.9rem 0; }

code, pre, kbd, samp {
  font-family: ui-monospace, SFMono-Regular, "SF Mono", Consolas,
    "Liberation Mono", monospace;
  font-size: 0.9em;
}

code {
  padding: 0.15em 0.4em;
  border-radius: 4px;
  background: var(--code-bg);
}

pre {
  padding: 1rem 1.2rem;
  border-radius: 8px;
  border: 1px solid var(--border);
  background: var(--code-bg);
  overflow-x: auto;
  line-height: 1.6;
}

pre code { padding: 0; background: none; }

blockquote {
  margin: 1.2rem 0;
  padding: 0.2rem 1.2rem;
  border-left: 0.25rem solid var(--accent);
  color: var(--muted);
  background: var(--soft-bg);
  border-radius: 0 6px 6px 0;
}

table {
  width: 100%;
  margin: 1.2rem 0;
  border-collapse: collapse;
  font-size: 0.95em;
}

th, td {
  padding: 0.45rem 0.8rem;
  border: 1px solid var(--border);
}

th { background: var(--soft-bg); }

img { max-width: 100%; }

hr {
  border: none;
  border-top: 1px solid var(--border);
  margin: 2.5rem 0;
}

ul, ol { padding-left: 1.5rem; }
li { margin: 0.3rem 0; }

footer {
  margin-top: 3.5rem;
  padding-top: 1.2rem;
  border-top: 1px solid var(--border);
  color: var(--muted);
  font-size: 0.9rem;
}
"""

INDEX_MD = """\
---
title: 首页
---

# 你好，世界

这里由 **mksite** 生成 —— 一个零依赖的纯 Python 静态站点生成器。

## 快速开始

```bash
# 修改 content/ 下的 Markdown 文件，然后：
mksite serve      # 本地预览 http://127.0.0.1:8000
mksite build      # 生成静态文件到 public/
```

## 最近文章

- [我的第一篇文章](posts/my-first-post.html)
"""

ABOUT_MD = """\
---
title: 关于
---

# 关于

这个站点由 [mksite](https://github.com/mksite) 生成。

在这里写点关于你自己或这个站点的内容。
"""

POST_MD = """\
---
title: {title}
date: {date}
tags: []
---

"""

GITIGNORE = """\
public/
__pycache__/
"""
