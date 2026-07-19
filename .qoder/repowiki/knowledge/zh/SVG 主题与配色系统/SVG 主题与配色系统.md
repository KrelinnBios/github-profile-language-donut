---
kind: frontend_style
name: SVG 主题与配色系统
category: frontend_style
scope:
    - '**'
source_files:
    - examples/language-donut.config.json
    - src/language_donut/chart.py
    - src/language_donut/colors.py
---

该仓库是一个 GitHub Action，核心产出是内嵌 SVG 的环形图。前端样式完全由 Python 运行时动态生成，不存在独立的 CSS/SCSS/Tailwind 等样式工程体系，而是通过 JSON 配置驱动的主题与颜色方案。

**主题系统（theme）**
- 在 `examples/language-donut.config.json` 中定义 `theme.light_*` / `theme.dark_*` 两组色板：文本、次要文本、轨道底色。
- 生成的 SVG 内部 `<style>` 块默认使用 light 主题，并通过 `@media (prefers-color-scheme: dark)` 媒体查询自动切换到 dark 主题，实现“暗色模式感知”。
- 字体采用系统栈 `-apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif`，字号与字重在 `.label`、`.percent`、`.center-value`、`.center-label` 等类中硬编码。

**语言配色（colors）**
- 用户可在 `colors` 字段为特定语言指定固定色值；未指定的语言会回退到 `src/language_donut/colors.py::generated_color()`，基于语言名的 SHA256 哈希映射到 HSL 色相，保证稳定且可区分。
- 所有语言色最终通过 `color_for(language, colors)` 解析后注入到 SVG `<path class="segment">` 的 `stroke` 属性以及图例圆点/进度条的 `fill` 属性。

**布局与尺寸**
- 图表尺寸、环形半径、图例列数/行高、是否显示进度条等全部来自 `chart.*` 配置键，由 `build_svg()` 计算后直接写入 SVG 的 `width`/`height`/`viewBox` 及元素坐标。
- 响应式策略依赖 SVG 自身的 `viewBox` + `prefers-color-scheme` 媒体查询，而非 CSS Grid/Flexbox 或外部框架。

**开发者约定**
- 新增视觉变量应优先添加到 `theme` 对象并在 `build_svg` 的 `<style>` 模板中引用，避免散落到字符串拼接中。
- 自定义语言色应在 `colors` 中声明，不要修改 `generated_color` 的哈希算法，以免破坏已有图表的一致性。
- 如需扩展新的 SVG 元素样式，需同时提供 light/dark 两套填充值以维持暗色模式兼容。