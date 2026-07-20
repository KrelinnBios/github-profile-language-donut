#!/usr/bin/env python3
"""SVG chart generation and geometry for language donut."""
import html
import math

from .colors import color_for, displayed_languages, percentage_label


def polar_to_cartesian(center_x, center_y, radius, angle):
    return (
        center_x + radius * math.cos(angle),
        center_y + radius * math.sin(angle),
    )


def divider_control_point(center_x, center_y, inner_radius, outer_radius, angle, curve_offset):
    """Return the shared control point for one curved divider."""
    mid_radius = (inner_radius + outer_radius) / 2
    base_x, base_y = polar_to_cartesian(center_x, center_y, mid_radius, angle)
    tangent_x = -math.sin(angle)
    tangent_y = math.cos(angle)
    return (
        base_x + curve_offset * tangent_x,
        base_y + curve_offset * tangent_y,
    )


def full_ring_path(center_x, center_y, inner_radius, outer_radius, start_angle):
    """Return a path for a full annulus using two half-circle arcs."""
    mid_angle = start_angle + math.pi
    outer_start_x, outer_start_y = polar_to_cartesian(center_x, center_y, outer_radius, start_angle)
    outer_mid_x, outer_mid_y = polar_to_cartesian(center_x, center_y, outer_radius, mid_angle)
    inner_start_x, inner_start_y = polar_to_cartesian(center_x, center_y, inner_radius, start_angle)
    inner_mid_x, inner_mid_y = polar_to_cartesian(center_x, center_y, inner_radius, mid_angle)
    return (
        f"M {outer_start_x:.2f} {outer_start_y:.2f} "
        f"A {outer_radius:.2f} {outer_radius:.2f} 0 1 1 {outer_mid_x:.2f} {outer_mid_y:.2f} "
        f"A {outer_radius:.2f} {outer_radius:.2f} 0 1 1 {outer_start_x:.2f} {outer_start_y:.2f} "
        f"L {inner_start_x:.2f} {inner_start_y:.2f} "
        f"A {inner_radius:.2f} {inner_radius:.2f} 0 1 0 {inner_mid_x:.2f} {inner_mid_y:.2f} "
        f"A {inner_radius:.2f} {inner_radius:.2f} 0 1 0 {inner_start_x:.2f} {inner_start_y:.2f} Z"
    )


def annular_segment_path(center_x, center_y, inner_radius, outer_radius, start_angle, end_angle, curve_offset):
    """Return one filled, contiguous donut segment with curved shared dividers."""
    sweep = max(0.0, float(end_angle) - float(start_angle))
    if sweep <= 0:
        return ""
    if sweep >= math.tau - 1e-6:
        return full_ring_path(center_x, center_y, inner_radius, outer_radius, start_angle)

    outer_start_x, outer_start_y = polar_to_cartesian(center_x, center_y, outer_radius, start_angle)
    outer_end_x, outer_end_y = polar_to_cartesian(center_x, center_y, outer_radius, end_angle)
    inner_start_x, inner_start_y = polar_to_cartesian(center_x, center_y, inner_radius, start_angle)
    inner_end_x, inner_end_y = polar_to_cartesian(center_x, center_y, inner_radius, end_angle)
    end_control_x, end_control_y = divider_control_point(center_x, center_y, inner_radius, outer_radius, end_angle, curve_offset)
    start_control_x, start_control_y = divider_control_point(center_x, center_y, inner_radius, outer_radius, start_angle, curve_offset)
    large_arc = 1 if sweep > math.pi else 0

    return (
        f"M {outer_start_x:.2f} {outer_start_y:.2f} "
        f"A {outer_radius:.2f} {outer_radius:.2f} 0 {large_arc} 1 {outer_end_x:.2f} {outer_end_y:.2f} "
        f"Q {end_control_x:.2f} {end_control_y:.2f} {inner_end_x:.2f} {inner_end_y:.2f} "
        f"A {inner_radius:.2f} {inner_radius:.2f} 0 {large_arc} 0 {inner_start_x:.2f} {inner_start_y:.2f} "
        f"Q {start_control_x:.2f} {start_control_y:.2f} {outer_start_x:.2f} {outer_start_y:.2f} Z"
    )


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
    height = max(int(chart["min_height"]), int(chart["vertical_padding"] + display_rows * row_height))

    legend_x = float(chart["legend_x"])
    legend_width = float(chart["legend_width"])
    column_gap = float(chart["legend_column_gap"])
    column_count = min(max_columns, max(1, math.ceil(len(items) / rows_per_column)))
    extra_width = (column_count - 1) * float(chart["two_column_extra_width"])
    width = int(base_width + extra_width)
    expanded_legend_width = legend_width + extra_width
    column_width = (expanded_legend_width - (column_count - 1) * column_gap) / column_count

    center_x = float(chart["donut_center_x"]) + extra_width
    center_y = height / 2
    outer_radius = min(float(chart["donut_radius"]), (height - 36) / 2)
    ring_width = float(chart["donut_width"])
    inner_radius = max(0.0, outer_radius - ring_width)
    curve_offset = ring_width * 0.35

    dominant_language, dominant_bytes = items[0]
    dominant_percentage = dominant_bytes / total_bytes * 100

    segments = []
    progress_angle = 0.0
    start_angle_offset = -math.pi / 2
    for language, byte_count in items:
        sweep_angle = byte_count / total_bytes * math.tau
        start_angle = start_angle_offset + progress_angle
        end_angle = start_angle + sweep_angle
        path = annular_segment_path(center_x, center_y, inner_radius, outer_radius, start_angle, end_angle, curve_offset)
        if path:
            segments.append(f'    <path class="segment" d="{path}" fill="{color_for(language, colors)}" />')
        progress_angle += sweep_angle

    show_bars = bool(chart["show_bars"])
    item_extent = 21 if show_bars else 13
    legend_height = (display_rows - 1) * row_height + item_extent
    first_row_y = center_y - legend_height / 2 + 9 + float(chart["legend_vertical_offset"])

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
            f'    <text class="percent" x="{percent_x:.1f}" y="{y:.1f}" text-anchor="end">{percentage_label(value)}</text>',
        ]
        if show_bars:
            row.extend([
                f'    <rect class="bar-track" x="{label_x:.1f}" y="{y + 9:.1f}" width="{bar_width:.1f}" height="3" rx="1.5"/>',
                f'    <rect x="{label_x:.1f}" y="{y + 9:.1f}" width="{max(4.0, bar_width * value / 100):.2f}" height="3" rx="1.5" fill="{color}"/>',
            ])
        legend_rows.extend(row)

    description = html.escape("Language mix across current public repositories: " + ", ".join(f"{language} {percentage_label(byte_count / total_bytes * 100)}" for language, byte_count in items) + ".")
    center_text = ""
    if chart["show_center_label"]:
        center_text = (
            f'  <text class="center-value" x="{center_x:.1f}" y="{center_y - 2:.1f}">{percentage_label(dominant_percentage)}</text>\n'
            f'  <text class="center-label" x="{center_x:.1f}" y="{center_y + 19:.1f}">{html.escape(dominant_language)}</text>\n'
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
     .donut-track {{ fill: {theme["light_track"]}; opacity: 0.20; }}
     .segment {{ stroke: none; }}
     @media (prefers-color-scheme: dark) {{
       .label, .center-value, .center-label {{ fill: {theme["dark_text"]}; }}
       .percent {{ fill: {theme["dark_muted"]}; }}
       .bar-track {{ fill: {theme["dark_track"]}; }}
       .donut-track {{ fill: {theme["dark_track"]}; }}
     }}
   </style>
   <g>
 {chr(10).join(legend_rows)}
   </g>
   <g>
     <path class="donut-track" d="{full_ring_path(center_x, center_y, inner_radius, outer_radius, start_angle_offset)}" />
 {chr(10).join(segments)}
   </g>
 {center_text}</svg>'''
