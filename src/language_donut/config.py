import json
from pathlib import Path

DEFAULT_CHART = {
    "width": 525,
    "min_height": 188,
    "vertical_padding": 28,
    "row_height": 32,
    "legend_x": 20,
    "legend_width": 256,
    "legend_column_gap": 20,
    "two_column_extra_width": 90,
    "legend_rows_per_column": 5,
    "legend_max_columns": 2,
    "legend_vertical_offset": 6,
    "donut_center_x": 418,
    "donut_radius": 72,
    "donut_width": 22,
    "min_segment_percentage": 1.0,
    "round_segment_threshold": 5,
    "show_bars": True,
    "show_center_label": True,
}

DEFAULT_THEME = {
    "light_text": "#24292f",
    "light_muted": "#57606a",
    "light_track": "#d0d7de",
    "dark_text": "#f0f6fc",
    "dark_muted": "#8b949e",
    "dark_track": "#30363d",
}

DEFAULT_COLORS = {
    "Kotlin": "#7F52FF", "HTML": "#E34F26", "JavaScript": "#F7DF1E",
    "CSS": "#00B8D9", "TypeScript": "#3178C6", "Python": "#22C55E",
    "PowerShell": "#EC4899", "Shell": "#89E051", "Java": "#B07219",
    "Swift": "#F05138", "Dart": "#00B4AB", "Go": "#00ADD8",
    "Rust": "#DEA584", "C": "#555555", "C++": "#F34B7D",
    "C#": "#178600", "Ruby": "#701516", "PHP": "#4F5D95",
    "Vue": "#41B883", "Svelte": "#FF3E00", "Lua": "#000080",
    "R": "#198CE7", "Other": "#8B949E",
}


def load_config(config_path: Path):
    raw = {}
    if config_path.exists():
        raw = json.loads(config_path.read_text(encoding="utf-8-sig"))

    chart = DEFAULT_CHART.copy()
    chart.update(raw.get("chart", {}))
    chart["donut_center_x"] = chart.get("ring_center_x", chart["donut_center_x"])
    chart["donut_radius"] = chart.get("ring_radius", chart["donut_radius"])
    chart["donut_width"] = chart.get("ring_width", chart["donut_width"])

    theme = DEFAULT_THEME.copy()
    theme.update(raw.get("theme", {}))
    colors = DEFAULT_COLORS.copy()
    colors.update(raw.get("colors", {}))

    return {
        "owner": raw.get("owner", ""),
        "profile_repository": raw.get("profile_repository", ""),
        "excluded_repositories": set(raw.get("excluded_repositories", [])),
        "include_archived": bool(raw.get("include_archived", False)),
        "include_forks": bool(raw.get("include_forks", False)),
        "max_languages": int(
            raw.get("max_named_languages", raw.get("max_languages", 9))
        ),
        "chart": chart,
        "theme": theme,
        "colors": colors,
    }
