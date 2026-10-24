# 贡献指南

感谢关注 mksite！这个项目刻意保持小巧，提交前请先认同一个原则：
**能用标准库解决的，不引入第三方依赖。**

## 开发流程

```bash
git clone https://github.com/USER/mksite.git
cd mksite
python -m unittest discover -s tests   # 全部测试应通过
```

1. Fork 仓库并新建分支（`git checkout -b my-feature`）。
2. 修改代码，为新行为补测试用例（`tests/` 下）。
3. 运行 `python -m unittest discover -s tests`，确保全部通过。
4. 提交 PR，并在描述里说明动机和改动范围。

## 代码风格

- 纯标准库；Python 3.9+ 兼容（不要用 3.10+ 才有的语法）。
- 单元测试放在 `tests/`，使用 `unittest`，不引入 pytest。
- 保持模块职责单一：解析在 `markdown.py`/`frontmatter.py`，管线在 `build.py`。

## 报告问题

提交 Issue 时请附上：最小复现的 Markdown 片段或命令、
Python 版本（`python --version`）、期望行为与实际行为。
