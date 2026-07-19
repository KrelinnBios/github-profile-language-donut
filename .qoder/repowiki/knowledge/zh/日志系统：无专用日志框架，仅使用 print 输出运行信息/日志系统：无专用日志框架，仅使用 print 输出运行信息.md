---
kind: logging_system
name: 日志系统：无专用日志框架，仅使用 print 输出运行信息
category: logging_system
scope:
    - '**'
source_files:
    - src/generate.py
---

该仓库未引入任何专用日志框架（如 Python `logging`、`loguru`、`structlog` 等），也未定义统一的 logger 实例或日志级别策略。整个应用仅在入口脚本 `src/generate.py` 的 `main()` 函数末尾通过一行 `print(...)` 输出 SVG 生成结果及变更状态，其余模块（`language_donut/chart.py`、`config.py`、`github.py`、`output.py`）均不产生任何结构化或分级日志输出。错误处理依赖异常冒泡至 GitHub Actions 工作流，由 CI 平台捕获并展示在任务日志中。因此，本项目不存在可抽象的“日志系统”，不符合 logging_system 类别的适用条件。