---
kind: configuration_system
name: JSON 配置文件与 GitHub Action 输入参数体系
category: configuration_system
scope:
    - '**'
source_files:
    - src/language_donut/config.py
    - examples/language-donut.config.json
    - action.yml
    - src/generate.py
---

本仓库采用「JSON 配置文件 + GitHub Action inputs」双层配置模型，用于控制语言环形图生成行为。

## 1. 配置来源与加载顺序

- 主入口：src/generate.py 通过 argparse 解析 CLI 参数（--config、--readme、--output-directory、--output-prefix），默认值与 action.yml 中同名 input 保持一致。
- 配置文件：src/language_donut/config.py::load_config() 读取 JSON 文件，不存在时回退到内置默认值；最终返回合并后的扁平字典。
- Action 层：action.yml 将 github-token、config-path、readme-path、output-directory、output-prefix 暴露为 inputs，并以环境变量 GITHUB_TOKEN 注入运行步骤。

加载优先级（由低到高）：内置默认 -> JSON 文件覆盖 -> CLI/Action inputs 覆盖。

## 2. 配置结构约定

language-donut.config.json 顶层字段：
- owner / profile_repository: string，目标用户与 README 所在仓库名
- excluded_repositories: string[]，排除统计的仓库列表
- include_archived / include_forks: bool，是否纳入归档/fork 仓库
- max_named_languages / max_languages: int，显示的语言数量上限（兼容旧键）
- chart.*: object，图表尺寸、图例布局、圆环几何等渲染参数
- theme.*: object，light/dark 主题色板
- colors.*: object，各语言颜色映射，未定义则回退内置 DEFAULT_COLORS

Chart 子段同时支持历史别名键 ring_center_x、ring_radius、ring_width，在加载时自动映射到 donut_* 新键。

## 3. 默认值策略

config.py 内嵌三组常量：DEFAULT_CHART、DEFAULT_THEME、DEFAULT_COLORS。load_config 对每个子段执行 dict.update(raw.get(...)) 实现浅合并，因此只需在 JSON 中声明需要覆盖的键即可。

## 4. 开发者约定

- 新增配置项应在 DEFAULT_* 常量中提供默认值，并在 load_config 的合并逻辑中注册。
- 如需废弃旧键，沿用现有模式：保留别名键并做映射，避免破坏既有 workflow。
- Action inputs 与 CLI 默认值应保持同步更新，确保本地调试与 CI 行为一致。
- 敏感凭据（GitHub Token）仅通过 action.yml 的 inputs.github-token 以环境变量传入，不应写入 JSON 配置。