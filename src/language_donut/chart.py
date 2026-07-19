<<<<<<< HEAD
import html
import math

from .colors import color_for, displayed_languages, percentage_label


def segment_percentages(items, total_bytes, minimum_percentage):
    actual = [byte_count / total_bytes * 100 for _, byte_count in items]
    minimum = max(0.0, float(minimum_percentage))
    tiny = [0 < value < minimum for value in actual]
    reserved = sum(tiny) * minimum
    scalable_total = sum(value for value, is_tiny in zip(actual, tiny) if not is_tiny)

    if not any(tiny) or reserved >= 100 or scalable_total <= 0:
        return actual, actual

    scale = (100 - reserved) / scalable_total
    visible = [
        minimum if is_tiny else value * scale
        for value, is_tiny in zip(actual, tiny)
    ]
    return actual, visible


def segment_stroke_geometry(segment_length, stroke_width, gap, rounded):
    """Return line cap, dash length, and dash-start inset for one segment.

    A round SVG stroke cap extends half a stroke width beyond each end of the
    dash. The dash therefore has to be shortened and moved forward so its
    painted shape stays inside the segment's angular allocation. Without this
    compensation, the first large segment wraps across the circle origin and
    intrudes into the tiny segments drawn immediately before it.
    """
    segment_length = max(0.0, float(segment_length))
    stroke_width = max(0.0, float(stroke_width))
    requested_gap = max(0.0, float(gap))

    if rounded and segment_length > stroke_width:
        minimum_dash = min(0.1, segment_length - stroke_width)
        available_gap = max(0.0, segment_length - stroke_width - minimum_dash)
        effective_gap = min(requested_gap, available_gap)
        dash_length = segment_length - stroke_width - effective_gap
        start_inset = effective_gap / 2 + stroke_width / 2
        return "round", dash_length, start_inset

    minimum_dash = min(0.1, segment_length)
    effective_gap = min(requested_gap, max(0.0, segment_length - minimum_dash))
    dash_length = segment_length - effective_gap
    return "butt", dash_length, effective_gap / 2


def build_svg(totals, config):
    total_bytes = sum(totals.values())
    chart = config["chart"]
    theme = config["theme"]
    colors = config["colors"]

    rows_per_column = max(1, int(chart.get("legend_rows_per_column", 5)))
    max_columns = max(1, int(chart.get("legend_max_columns", 2)))
    capacity = rows_per_column * max_columns
    named_limit = max(1, capacity - 1)
    if config["max_languages"] > 0:
        named_limit = min(config["max_languages"], named_limit)
    items = displayed_languages(totals, named_limit)

    base_width = int(chart["width"])
    row_height = float(chart["row_height"])
    display_rows = min(len(items), rows_per_column)
    height = max(
        int(chart["min_height"]),
        int(chart["vertical_padding"] + display_rows * row_height),
    )

    legend_x = float(chart["legend_x"])
    legend_width = float(chart["legend_width"])
    column_gap = float(chart["legend_column_gap"])
    column_count = min(max_columns, max(1, math.ceil(len(items) / rows_per_column)))
    extra_width = (column_count - 1) * float(chart["two_column_extra_width"])
    width = int(base_width + extra_width)
    expanded_legend_width = legend_width + extra_width
    column_width = (
        expanded_legend_width - (column_count - 1) * column_gap
    ) / column_count

    center_x = float(chart["donut_center_x"]) + extra_width
    center_y = height / 2
    radius = min(float(chart["donut_radius"]), (height - 36) / 2)
    stroke_width = float(chart["donut_width"])
    circumference = 2 * math.pi * radius
    dominant_language, dominant_bytes = items[0]
    dominant_percentage = dominant_bytes / total_bytes * 100
    actual_percentages, visible_percentages = segment_percentages(
        items,
        total_bytes,
        chart.get("min_segment_percentage", 0.8),
    )
    round_threshold = max(0.0, float(chart.get("round_segment_threshold", 5)))

    segments = []
    progress = 0.0
    for (language, _), actual_percentage, visible_percentage in zip(
        items, actual_percentages, visible_percentages
    ):
        segment_length = visible_percentage / 100 * circumference
        gap = min(3.0, segment_length * 0.18)
        linecap, visible_length, start_inset = segment_stroke_geometry(
            segment_length,
            stroke_width,
            gap,
            actual_percentage >= round_threshold,
        )
        segments.append(
            f'    <circle class="segment" cx="{center_x:.1f}" cy="{center_y:.1f}" '
            f'r="{radius:.1f}" stroke="{color_for(language, colors)}" '
            f'stroke-linecap="{linecap}" '
            f'stroke-dasharray="{visible_length:.2f} {circumference - visible_length:.2f}" '
            f'stroke-dashoffset="{-progress - start_inset:.2f}"/>'
        )
        progress += segment_length

    show_bars = bool(chart["show_bars"])
    item_extent = 21 if show_bars else 13
    legend_height = (display_rows - 1) * row_height + item_extent
    first_row_y = (
        center_y
        - legend_height / 2
        + 9
        + float(chart["legend_vertical_offset"])
    )
    legend_rows = []
    for index, (language, byte_count) in enumerate(items):
        value = byte_count / total_bytes * 100
        column_index = index // rows_per_column
        row_index = index % rows_per_column
        column_x = legend_x + column_index * (column_width + column_gap)
        label_x = column_x + 24
        percent_x = column_x + column_width
        bar_width = percent_x - label_x
        y = first_row_y + row_index * row_height
        color = color_for(language, colors)
        row = [
            f'    <circle cx="{column_x + 6:.1f}" cy="{y - 4:.1f}" r="5" fill="{color}"/>',
            f'    <text class="label" x="{label_x:.1f}" y="{y:.1f}">{html.escape(language)}</text>',
            f'    <text class="percent" x="{percent_x:.1f}" y="{y:.1f}" '
            f'text-anchor="end">{percentage_label(value)}</text>',
        ]
        if show_bars:
            row.extend(
                [
                    f'    <rect class="bar-track" x="{label_x:.1f}" y="{y + 9:.1f}" '
                    f'width="{bar_width:.1f}" height="3" rx="1.5"/>',
                    f'    <rect x="{label_x:.1f}" y="{y + 9:.1f}" '
                    f'width="{max(2.0, bar_width * value / 100):.2f}" height="3" '
                    f'rx="1.5" fill="{color}"/>',
                ]
            )
        legend_rows.extend(row)

    description = html.escape(
        "Language mix across current public repositories: "
        + ", ".join(
            f"{language} {percentage_label(byte_count / total_bytes * 100)}"
            for language, byte_count in items
        )
        + "."
    )

    center_text = ""
    if chart["show_center_label"]:
        center_text = (
            f'  <text class="center-value" x="{center_x:.1f}" '
            f'y="{center_y - 2:.1f}">{percentage_label(dominant_percentage)}</text>\n'
            f'  <text class="center-label" x="{center_x:.1f}" '
            f'y="{center_y + 19:.1f}">{html.escape(dominant_language)}</text>\n'
        )

    return f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">
  <title id="title">Language distribution donut chart</title>
  <desc id="desc">{description}</desc>
  <style>
    .label {{ fill: {theme["light_text"]}; font: 600 14px -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; }}
    .percent {{ fill: {theme["light_muted"]}; font: 600 13px -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; }}
    .center-value {{ fill: {theme["light_text"]}; font: 700 28px -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; text-anchor: middle; }}
    .center-label {{ fill: {theme["light_text"]}; font: 600 13px -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; text-anchor: middle; }}
    .bar-track {{ fill: {theme["light_track"]}; opacity: 0.34; }}
    .donut-track {{ stroke: {theme["light_track"]}; opacity: 0.20; }}
    .segment {{ fill: none; stroke-width: {stroke_width:g}; }}
    @media (prefers-color-scheme: dark) {{
      .label, .center-value, .center-label {{ fill: {theme["dark_text"]}; }}
      .percent {{ fill: {theme["dark_muted"]}; }}
      .bar-track {{ fill: {theme["dark_track"]}; }}
      .donut-track {{ stroke: {theme["dark_track"]}; }}
    }}
  </style>

  <g>
{chr(10).join(legend_rows)}
  </g>

  <g transform="rotate(-90 {center_x:.1f} {center_y:.1f})">
    <circle class="donut-track" cx="{center_x:.1f}" cy="{center_y:.1f}" r="{radius:.1f}" fill="none" stroke-width="{stroke_width:g}"/>
{chr(10).join(segments)}
  </g>
{center_text}</svg>
'''
=======
import html
import math

from .colors import color_for, displayed_languages, percentage_label


def segment_percentages(items, total_bytes, minimum_percentage):
    actual = [byte_count / total_bytes * 100 for _, byte_count in items]
    minimum = max(0.0, float(minimum_percentage))
    tiny = [0 < value < minimum for value in actual]
    reserved = sum(tiny) * minimum
    scalable_total = sum(value for value, is_tiny in zip(actual, tiny) if not is_tiny)

    if not any(tiny) or reserved >= 100 or scalable_total <= 0:
        return actual, actual

    scale = (100 - reserved) / scalable_total
    visible = [
        minimum if is_tiny else value * scale
        for value, is_tiny in zip(actual, tiny)
    ]
    return actual, visible


def segment_stroke_geometry(segment_length, stroke_width, gap, rounded):
    """Return line cap, dash length, and dash-start inset for one segment.

    A round SVG stroke cap extends half a stroke width beyond each end of the
    dash. The dash therefore has to be shortened and moved forward so its
    painted shape stays inside the segment's angular allocation. Without this
    compensation, the first large segment wraps across the circle origin and
    intrudes into the tiny segments drawn immediately before it.
    """
    segment_length = max(0.0, float(segment_length))
    stroke_width = max(0.0, float(stroke_width))
    requested_gap = max(0.0, float(gap))

    if rounded and segment_length > stroke_width:
        minimum_dash = min(0.1, segment_length - stroke_width)
        available_gap = max(0.0, segment_length - stroke_width - minimum_dash)
        effective_gap = min(requested_gap, available_gap)
        dash_length = segment_length - stroke_width - effective_gap
        start_inset = effective_gap / 2 + stroke_width / 2
        return "round", dash_length, start_inset

    minimum_dash = min(0.1, segment_length)
    effective_gap = min(requested_gap, max(0.0, segment_length - minimum_dash))
    dash_length = segment_length - effective_gap
    return "butt", dash_length, effective_gap / 2


def build_svg(totals, config):
    total_bytes = sum(totals.values())
    chart = config["chart"]
    theme = config["theme"]
    colors = config["colors"]

    rows_per_column = max(1, int(chart.get("legend_rows_per_column", 5)))
    max_columns = max(1, int(chart.get("legend_max_columns", 2)))
    capacity = rows_per_column * max_columns
    named_limit = max(1, capacity - 1)
    if config["max_languages"] > 0:
        named_limit = min(config["max_languages"], named_limit)
    items = displayed_languages(totals, named_limit)

    base_width = int(chart["width"])
    row_height = float(chart["row_height"])
    display_rows = min(len(items), rows_per_column)
    height = max(
        int(chart["min_height"]),
        int(chart["vertical_padding"] + display_rows * row_height),
    )

    legend_x = float(chart["legend_x"])
    legend_width = float(chart["legend_width"])
    column_gap = float(chart["legend_column_gap"])
    column_count = min(max_columns, max(1, math.ceil(len(items) / rows_per_column)))
    extra_width = (column_count - 1) * float(chart["two_column_extra_width"])
    width = int(base_width + extra_width)
    expanded_legend_width = legend_width + extra_width
    column_width = (
        expanded_legend_width - (column_count - 1) * column_gap
    ) / column_count

    center_x = float(chart["donut_center_x"]) + extra_width
    center_y = height / 2
    radius = min(float(chart["donut_radius"]), (height - 36) / 2)
    stroke_width = float(chart["donut_width"])
    circumference = 2 * math.pi * radius
    dominant_language, dominant_bytes = items[0]
    dominant_percentage = dominant_bytes / total_bytes * 100
    actual_percentages, visible_percentages = segment_percentages(
        items,
        total_bytes,
        chart.get("min_segment_percentage", 0.8),
    )
    round_threshold = max(0.0, float(chart.get("round_segment_threshold", 5)))

    segments = []
    progress = 0.0
    for (language, _), actual_percentage, visible_percentage in zip(
        items, actual_percentages, visible_percentages
    ):
        segment_length = visible_percentage / 100 * circumference
        gap = min(3.0, segment_length * 0.18)
        linecap, visible_length, start_inset = segment_stroke_geometry(
            segment_length,
            stroke_width,
            gap,
            actual_percentage >= round_threshold,
        )
        segments.append(
            f'    <circle class="segment" cx="{center_x:.1f}" cy="{center_y:.1f}" '
            f'r="{radius:.1f}" stroke="{color_for(language, colors)}" '
            f'stroke-linecap="{linecap}" '
            f'stroke-dasharray="{visible_length:.2f} {circumference - visible_length:.2f}" '
            f'stroke-dashoffset="{-progress - start_inset:.2f}"/>'
        )
        progress += segment_length

    show_bars = bool(chart["show_bars"])
    item_extent = 21 if show_bars else 13
    legend_height = (display_rows - 1) * row_height + item_extent
    first_row_y = (
        center_y
        - legend_height / 2
        + 9
        + float(chart["legend_vertical_offset"])
    )
    legend_rows = []
    for index, (language, byte_count) in enumerate(items):
        value = byte_count / total_bytes * 100
        column_index = index // rows_per_column
        row_index = index % rows_per_column
        column_x = legend_x + column_index * (column_width + column_gap)
        label_x = column_x + 24
        percent_x = column_x + column_width
        bar_width = percent_x - label_x
        y = first_row_y + row_index * row_height
        color = color_for(language, colors)
        row = [
            f'    <circle cx="{column_x + 6:.1f}" cy="{y - 4:.1f}" r="5" fill="{color}"/>',
            f'    <text class="label" x="{label_x:.1f}" y="{y:.1f}">{html.escape(language)}</text>',
            f'    <text class="percent" x="{percent_x:.1f}" y="{y:.1f}" '
            f'text-anchor="end">{percentage_label(value)}</text>',
        ]
        if show_bars:
            row.extend(
                [
                    f'    <rect class="bar-track" x="{label_x:.1f}" y="{y + 9:.1f}" '
                    f'width="{bar_width:.1f}" height="3" rx="1.5"/>',
                    f'    <rect x="{label_x:.1f}" y="{y + 9:.1f}" '
                    f'width="{max(2.0, bar_width * value / 100):.2f}" height="3" '
                    f'rx="1.5" fill="{color}"/>',
                ]
            )
        legend_rows.extend(row)

    description = html.escape(
        "Language mix across current public repositories: "
        + ", ".join(
            f"{language} {percentage_label(byte_count / total_bytes * 100)}"
            for language, byte_count in items
        )
        + "."
    )

    center_text = ""
    if chart["show_center_label"]:
        center_text = (
            f'  <text class="center-value" x="{center_x:.1f}" '
            f'y="{center_y - 2:.1f}">{percentage_label(dominant_percentage)}</text>\n'
            f'  <text class="center-label" x="{center_x:.1f}" '
            f'y="{center_y + 19:.1f}">{html.escape(dominant_language)}</text>\n'
        )

    return f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">
  <title id="title">Language distribution donut chart</title>
  <desc id="desc">{description}</desc>
  <style>
    .label {{ fill: {theme["light_text"]}; font: 600 14px -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; }}
    .percent {{ fill: {theme["light_muted"]}; font: 600 13px -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; }}
    .center-value {{ fill: {theme["light_text"]}; font: 700 28px -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; text-anchor: middle; }}
    .center-label {{ fill: {theme["light_text"]}; font: 600 13px -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; text-anchor: middle; }}
    .bar-track {{ fill: {theme["light_track"]}; opacity: 0.34; }}
    .donut-track {{ stroke: {theme["light_track"]}; opacity: 0.20; }}
    .segment {{ fill: none; stroke-width: {stroke_width:g}; }}
    @media (prefers-color-scheme: dark) {{
      .label, .center-value, .center-label {{ fill: {theme["dark_text"]}; }}
      .percent {{ fill: {theme["dark_muted"]}; }}
      .bar-track {{ fill: {theme["dark_track"]}; }}
      .donut-track {{ stroke: {theme["dark_track"]}; }}
    }}
  </style>

  <g>
{chr(10).join(legend_rows)}
  </g>

  <g transform="rotate(-90 {center_x:.1f} {center_y:.1f})">
    <circle class="donut-track" cx="{center_x:.1f}" cy="{center_y:.1f}" r="{radius:.1f}" fill="none" stroke-width="{stroke_width:g}"/>
{chr(10).join(segments)}
  </g>
{center_text}</svg>
'''
>>>>>>> 23b6d9dccb1f19b39219aee4f0a0b2a3b8f1939d
