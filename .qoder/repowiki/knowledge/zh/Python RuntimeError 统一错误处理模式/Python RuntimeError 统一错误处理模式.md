---
kind: error_handling
name: Python RuntimeError 统一错误处理模式
category: error_handling
scope:
    - '**'
source_files:
    - src/language_donut/github.py
    - src/language_donut/output.py
    - src/generate.py
---

该仓库采用 Python 内置 RuntimeError 作为统一的错误抛出方式，未定义自定义异常类型或错误码体系。所有业务层错误均通过 raise RuntimeError(...) 直接向上冒泡，由顶层入口脚本 src/generate.py 的 main() 函数自然暴露给 GitHub Actions 运行时，由 Action 框架捕获并终止流程。

关键特征：
- 网络请求错误：在 src/language_donut/github.py 中，对 urllib.error.HTTPError 进行显式捕获，包装为包含 HTTP 状态码、请求路径和响应体的 RuntimeError，并通过 from error 保留原始异常链以便调试。
- 配置/参数校验错误：在 src/language_donut/output.py 中对 output-prefix 使用正则全匹配校验，不合法时抛出带中文提示的 RuntimeError；同时检查 README 文件是否存在以及是否包含预期的图片引用占位符，缺失时给出明确修复指引。
- 业务数据完整性错误：当 GitHub API 返回空语言数据（如用户无公开仓库）时，抛出说明性 RuntimeError。
- 顶层无 try/except 包裹：generate.py 的 main() 不做任何异常捕获，依赖 GitHub Actions 的错误输出机制展示堆栈信息。

约定与约束：
- 所有错误消息均为中文，面向最终使用者而非开发者。
- 未使用日志记录，错误信息仅通过标准输出和异常堆栈传递。
- 没有 panic/recover 机制（Python 本身无此概念），也未使用中间件模式集中处理错误。