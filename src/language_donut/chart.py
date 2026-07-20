#!/usr/bin/env python3
"""SVG chart generation and geometry for language donut."""
import html
import math

from .colors import color_for, displayed_languages, percentage_label


def segment_percentages(items, total_bytes, minimum_percentage):
    actual = [byte_count / total_bytes * 100 for _, byte_count in items]
    minimum = max(0.0, float(minimum_percentage))

    if minimum <= 0:
        return actual, actual, [False] * len(actual)

    # Tiered floor: ≤ min -> dot; min..2*min -> boosted to 2*min; >=2*min -> leave for scaling.
    upper = minimum * 2
    dot_threshold = minimum

    def effective(value):
        if value <= 0:
            return 0.0
        if value <= dot_threshold:
            return "DOT"       # explicit sentinel for dot items
        if value < upper:
            return upper      # boost small-but-visible items to upper
        return None           # None means: treat as normal/scalable

    boosted = []
    for v in actual:
        e = effective(v)
        if e == 0.0:
            boosted.append(0.0)
        else:
            boosted.append(e)

    # is_dot: True for items explicitly marked as DOT
    is_dot = [b == "DOT" for b in boosted]
    # reserved: sum of explicit boosted values (numbers), exclude DOT and None
    reserved = sum(b for b in boosted if isinstance(b, (int, float)) and b > 0)
    # scalable_total: sum of actual percentages for non-dot items that will be scaled
    scalable_total = sum(a for a, d in zip(actual, is_dot) if not d and a > 0)

    if not any(not d for d in is_dot) or reserved >= 100 or scalable_total <= 0:
        return actual, actual, [False] * len(actual)

    scale = (100 - reserved) / scalable_total
    visible = []
    for a, b, d in zip(actual, boosted, is_dot):
        if isinstance(b, (int, float)) and b > 0:
            visible.append(b)
        elif d:
            visible.append(0.0)
        else:
            visible.append(a * scale)
    return actual, visible, is_dot


def polar_to_cartesian(center_x, center_y, radius, angle):
    return (
        center_x + radius * math.cos(angle),
        center_y + radius * math.sin(angle),
    )


def describe_arc(center_x, center_y, radius, start_angle, end_angle):
    start_x, start_y = polar_to_cartesian(center_x, center_y, radius, start_angle)
    end_x, end_y = polar_to_cartesian(center_x, center_y, radius, end_angle)
    large_arc = 1 if end_angle - start_angle > math.pi else 0
    return (
        f"M {start_x:.2f} {start_y:.2f} "
        f"A {radius:.2f} {radius:.2f} 0 {large_arc} 1 {end_x:.2f} {end_y:.2f}"
    )


def segment_path_geometry(segment_angle, gap_angle, minimum_fraction=0.25):
    """Return (visible_angle, inset_angle) for one independent arc segment."""
    segment_angle = max(0.0, float(segment_angle))
    gap_angle = max(0.0, float(gap_angle))
    if segment_angle <= 0:
        return 0.0, 0.0

    visible_angle = max(segment_angle * minimum_fraction, segment_angle - gap_angle)
    visible_angle = min(segment_angle, visible_angle)
    inset_angle = max(0.0, (segment_angle - visible_angle) / 2)
    return visible_angle, inset_angle


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

    actual_percentages, visible_percentages, is_dot = segment_percentages(
        items,
        total_bytes,
        chart.get("min_segment_percentage", 0.5),
    )

    segments = []
    dots = []
    progress = 0.0
    start_angle_offset = -math.pi / 2

    # Place dot items as small circles at the bottom of the donut.
    dot_angle_offset = math.pi / 2  # bottom of circle
    dot_spacing = math.radians(5)  # 5° between dots
    dot_items = [(i, lang) for i, (lang, _) in enumerate(items) if is_dot[i]]
    dot_start = dot_angle_offset - (len(dot_items) - 1) * dot_spacing / 2 if dot_items else 0

    for idx, (language, _) in enumerate(items):
        color = color_for(language, colors)

        if is_dot[idx]:
            # Render as circle on the donut perimeter (diameter = stroke width).
            dot_pos = dot_items.index((idx, language))
            angle = dot_start + dot_pos * dot_spacing
            dx, dy = polar_to_cartesian(center_x, center_y, radius, angle)
            dot_r = stroke_width / 2
            dots.append(
                f'    <circle cx="{dx:.1f}" cy="{dy:.1f}" r="{dot_r:.1f}" '
                f'fill="{color}" />'
            )
            continue

        # Normal arc segment.
        visible_percentage = visible_percentages[idx]
        segment_length = visible_percentage / 100 * circumference
        segment_angle = segment_length / radius if radius > 0 else 0.0

        gap_length = min(3.0, segment_length * 0.18)
        gap_angle = gap_length / radius if radius > 0 else 0.0

        visible_angle, inset_angle = segment_path_geometry(segment_angle, gap_angle)

        start_angle = (
            start_angle_offset + progress / radius + inset_angle
            if radius > 0 else start_angle_offset
        )
        end_angle = start_angle + visible_angle

        path = describe_arc(center_x, center_y, radius, start_angle, end_angle)
        segments.append(
            f'    <path class="segment" d="{path}" '
            f'stroke="{color}" />'
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
            if is_dot[index]:
                # Dot item: show a small circle instead of a bar.
                row.append(
                    f'    <circle cx="{label_x + 4:.1f}" cy="{y + 10.5:.1f}" '
                    f'r="3" fill="{color}" />'
                )
            else:
                row.extend(
                    [
                        f'    <rect class="bar-track" x="{label_x:.1f}" y="{y + 9:.1f}" '
                        f'width="{bar_width:.1f}" height="3" rx="1.5"/>',
                        f'    <rect x="{label_x:.1f}" y="{y + 9:.1f}" '
                        f'width="{max(4.0, bar_width * value / 100):.2f}" height="3" '
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
     .segment {{ fill: none; stroke-width: {stroke_width:g}; stroke-linecap: round; }}
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

   <g>
     <circle class="donut-track" cx="{center_x:.1f}" cy="{center_y:.1f}" r="{radius:.1f}" fill="none" stroke-width="{stroke_width:g}"/>
 {chr(10).join(segments)}
 {chr(10).join(dots)}
   </g>
 {center_text}</svg>