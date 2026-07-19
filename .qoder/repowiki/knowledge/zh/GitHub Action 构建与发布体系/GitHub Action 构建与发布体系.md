---
kind: build_system
name: GitHub Action 构建与发布体系
category: build_system
scope:
    - '**'
source_files:
    - action.yml
    - .github/workflows/test.yml
---

本项目是一个纯 Python 实现的 GitHub Action，采用极简的“无依赖打包”策略：没有 Makefile、Dockerfile、pyproject.toml、requirements.txt 等任何构建脚本或包管理文件。整个 Action 由一个入口脚本 `src/generate.py` 和若干模块组成，通过 `action.yml` 以 composite runner 方式直接调用 Python 解释器执行。

**运行环境约定**
- 运行时要求宿主 Runner 已安装 Python（Action 未声明 `python-version`，依赖 GitHub-hosted Runner 自带的 Python）。
- 所有第三方依赖（如 `requests`、`matplotlib` 等）均未在仓库中显式声明，意味着它们必须随 Runner 预装或由用户自行提供。

**CI 流水线**
- `.github/workflows/test.yml` 仅在 push 到 main 和 PR 触发，使用 `python -m unittest discover -s tests -v` 运行单元测试，未包含 lint、类型检查或覆盖率步骤。
- 未定义 release 或 publish 工作流，版本发布不经过 CI 自动化。

**发布与分发模式**
- 该 Action 以源码形式直接在 GitHub 上引用（例如 `uses: KrelinnBios/github-profile-language-donut-action@v1`），无需打包成 Docker 镜像或发布到 PyPI。
- 版本号通过 Git tag 管理，用户在 workflow 中通过 `@vX.Y.Z` 引用特定版本。

**开发者约束**
- 新增依赖后需同步更新 README 中的环境说明，因为仓库不包含依赖清单。
- 测试仅覆盖核心逻辑，未在 CI 中引入多 Python 版本矩阵或集成测试。
- 由于是 composite action，所有可执行逻辑必须为纯 Python 且无需编译步骤。