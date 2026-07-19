---
kind: external_dependency
name: GitHub 平台与 API
slug: github
category: external_dependency
category_hints:
    - vendor_identity
    - auth_protocol
    - client_constraint
scope:
    - '**'
---

本项目作为 GitHub Action 运行，核心依赖 GitHub 平台提供的三项能力：
- GitHub REST API（`/users/{owner}/repos`、`/repos/{owner}/{repo}/languages`）用于拉取公开仓库列表及语言字节统计；API 版本通过 `X-GitHub-Api-Version: 2022-11-28` 固定。
- GitHub Actions 运行时环境，通过环境变量注入上下文（`GITHUB_REPOSITORY`、`GITHUB_REPOSITORY_OWNER`）与凭据（`GITHUB_TOKEN`），Action 以 composite runner 方式调用 Python 脚本。
- 认证协议为 Bearer Token，Token 来自 `GITHUB_TOKEN` 环境变量，请求头使用 `Authorization: Bearer <token>`。

集成要点：
- API 根地址可通过 `GITHUB_API_URL` 覆盖，默认 `https://api.github.com`，便于企业版或代理场景。
- 分页按每页 100 条轮询，直到返回不足 100 条为止。
- 跨仓库通知需额外创建仅授权个人主页仓库的 fine-grained PAT，并通过 `repository_dispatch` 事件触发主页更新工作流。

注意：项目声明“无第三方依赖”，除 Python 标准库外不引入任何 pip 包。