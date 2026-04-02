from __future__ import annotations

from datetime import date
from xml.sax.saxutils import escape

from .model import PlacedChart, PlacedTask, PlacedTrack

PALETTE = [
    "#1f6feb",
    "#f05d23",
    "#2a9d8f",
    "#8c5cf5",
    "#ffb703",
    "#e63946",
    "#4d908e",
    "#577590",
]


def render_svg(chart: PlacedChart, column_width: int | None = None, row_height: int = 34) -> str:
    total_columns = len(chart.axis.keys)
    column_width = choose_column_width(chart, column_width)
    label_width = estimate_label_width(chart)
    right_margin = 40
    top_margin = 92
    bottom_margin = 32
    track_gap = 8
    axis_height = 54
    chart_width = label_width + total_columns * column_width + right_margin
    tracks_height = sum(track.lane_count * row_height + track_gap for track in chart.tracks)
    chart_height = top_margin + axis_height + tracks_height + bottom_margin

    header_top = top_margin
    grid_top = top_margin + axis_height
    grid_right = label_width + total_columns * column_width

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{chart_width}" height="{chart_height}" '
        f'viewBox="0 0 {chart_width} {chart_height}" role="img" aria-labelledby="title desc">',
        f"<title>{escape(chart.title)}</title>",
        f"<desc>{escape(chart.title)} rendered across {escape(chart.axis.subtitle)}</desc>",
        "<style>",
        "text { font-family: Menlo, Consolas, monospace; fill: #122033; }",
        ".title { font-size: 24px; font-weight: 700; }",
        ".subtitle { font-size: 12px; fill: #526072; }",
        ".axis-title { font-size: 11px; font-weight: 700; fill: #526072; letter-spacing: 0.06em; }",
        ".track-label { font-size: 13px; font-weight: 700; }",
        ".axis-text { font-size: 12px; font-weight: 700; fill: #314255; }",
        ".bar-label { font-size: 12px; font-weight: 700; }",
        ".bar-label-outside { font-size: 12px; font-weight: 700; fill: #122033; }",
        "</style>",
        f'<rect width="{chart_width}" height="{chart_height}" fill="#f7f3ea" />',
        f'<rect x="0" y="0" width="{chart_width}" height="76" fill="#efe8d8" />',
        f'<text x="24" y="34" class="title">{escape(chart.title)}</text>',
        f'<text x="24" y="56" class="subtitle">{escape(chart.axis.subtitle)}</text>',
        f'<text x="{label_width}" y="{header_top - 12}" class="axis-title">{escape(chart.axis.title.upper())}</text>',
        f'<rect x="{label_width}" y="{header_top}" width="{total_columns * column_width}" height="{axis_height}" fill="#e9dfca" />',
    ]

    parts.extend(render_axis_headers(chart, label_width, header_top, axis_height, column_width))

    for column_index in range(total_columns + 1):
        x = label_width + column_index * column_width
        parts.append(
            f'<line x1="{x}" y1="{grid_top}" x2="{x}" y2="{chart_height - bottom_margin}" '
            f'stroke="#d8d1c2" stroke-width="1" />'
        )

    current_y = grid_top
    for track_index, track in enumerate(chart.tracks):
        current_y = _render_track(
            parts,
            chart,
            track,
            track_index,
            current_y,
            label_width,
            column_width,
            row_height,
            grid_right,
        )
        current_y += track_gap

    parts.append("</svg>")
    return "\n".join(parts)


def render_axis_headers(
    chart: PlacedChart,
    label_width: int,
    header_top: int,
    axis_height: int,
    column_width: int,
) -> list[str]:
    parts: list[str] = []
    for index, key in enumerate(chart.axis.keys):
        x = label_width + index * column_width
        fill = "#efe4ce" if index % 2 == 0 else "#e6dac1"
        parts.append(
            f'<rect x="{x}" y="{header_top}" width="{column_width}" height="{axis_height}" fill="{fill}" />'
        )
        parts.append(
            f'<line x1="{x}" y1="{header_top}" x2="{x}" y2="{header_top + axis_height}" stroke="#cabca1" stroke-width="1" />'
        )
        text_x = x + column_width / 2
        text_y = header_top + axis_height / 2 + 5
        parts.append(
            f'<text x="{text_x}" y="{text_y}" text-anchor="middle" class="axis-text">{escape(display_axis_label(chart, key))}</text>'
        )

    end_x = label_width + len(chart.axis.keys) * column_width
    parts.append(
        f'<line x1="{end_x}" y1="{header_top}" x2="{end_x}" y2="{header_top + axis_height}" stroke="#cabca1" stroke-width="1" />'
    )
    parts.append(
        f'<line x1="{label_width}" y1="{header_top + axis_height}" x2="{end_x}" y2="{header_top + axis_height}" '
        f'stroke="#cabca1" stroke-width="1" />'
    )
    return parts


def build_ascii_preview(chart: PlacedChart) -> str:
    if chart.axis.kind == "tag":
        return build_tag_preview(chart)
    return build_date_preview(chart)


def build_tag_preview(chart: PlacedChart) -> str:
    headers = "".join(f"{compact_axis_label(key):<4}" for key in chart.axis.keys)
    lines = [chart.title, f"Timeline: {chart.axis.subtitle}", "    " + headers]

    for track in chart.tracks:
        lines.append(f"[{track.name}]")
        grid = [["." for _ in chart.axis.keys] for _ in range(track.lane_count)]
        for task in sorted(track.tasks, key=lambda item: (item.lane, item.start, item.end, item.label)):
            for column_index in range(task.start, task.end + 1):
                grid[task.lane][column_index] = task.symbol
        for lane_index, row in enumerate(grid):
            rendered = "".join(f"{cell:<4}" for cell in row)
            lines.append(f"L{lane_index:<2} {rendered}")
        for task in sorted(track.tasks, key=lambda item: (item.start, item.end, item.label)):
            lines.append(f"{task.symbol}={task.label} {task.start_key}..{task.end_key}")

    return "\n".join(lines)


def build_date_preview(chart: PlacedChart) -> str:
    month_line = [" "] * len(chart.axis.keys)
    tens_line = [" "] * len(chart.axis.keys)
    ones_line = [" "] * len(chart.axis.keys)

    for index, key in enumerate(chart.axis.keys):
        current_day = date.fromisoformat(key)
        if index == 0 or current_day.day == 1:
            month = current_day.strftime("%b")
            for offset, char in enumerate(month):
                if index + offset >= len(chart.axis.keys):
                    break
                month_line[index + offset] = char
        if current_day.day >= 10:
            tens_line[index] = str(current_day.day // 10)
        ones_line[index] = str(current_day.day % 10)

    lines = [
        chart.title,
        f"Timeline: {chart.axis.subtitle}",
        "    " + "".join(month_line),
        "    " + "".join(tens_line),
        "    " + "".join(ones_line),
    ]

    for track in chart.tracks:
        lines.append(f"[{track.name}]")
        grid = [["." for _ in chart.axis.keys] for _ in range(track.lane_count)]
        for task in sorted(track.tasks, key=lambda item: (item.lane, item.start, item.end, item.label)):
            for column_index in range(task.start, task.end + 1):
                grid[task.lane][column_index] = task.symbol
        for lane_index, row in enumerate(grid):
            lines.append(f"L{lane_index:<2} " + "".join(row))
        for task in sorted(track.tasks, key=lambda item: (item.start, item.end, item.label)):
            lines.append(f"{task.symbol}={task.label} {task.start_key}..{task.end_key}")

    return "\n".join(lines)


def choose_column_width(chart: PlacedChart, column_width: int | None) -> int:
    if column_width is not None:
        return column_width
    if chart.axis.kind == "tag":
        return 132
    return 36


def estimate_label_width(chart: PlacedChart) -> int:
    longest = max((len(track.name) for track in chart.tracks), default=12)
    return min(max(240, longest * 8 + 40), 520)


def display_axis_label(chart: PlacedChart, key: str) -> str:
    if chart.axis.kind == "date":
        return date.fromisoformat(key).strftime("%b %d")
    return key


def compact_axis_label(label: str) -> str:
    lowered = label.lower()
    if lowered.startswith("week "):
        return "W" + label.split()[-1]
    return label[:4]


def _render_track(
    parts: list[str],
    chart: PlacedChart,
    track: PlacedTrack,
    track_index: int,
    current_y: int,
    label_width: int,
    column_width: int,
    row_height: int,
    grid_right: int,
) -> int:
    track_height = track.lane_count * row_height
    band_fill = "#fbf8f2" if track_index % 2 == 0 else "#f3ede2"
    parts.append(f'<rect x="0" y="{current_y}" width="{label_width}" height="{track_height}" fill="{band_fill}" />')
    parts.append(
        f'<rect x="{label_width}" y="{current_y}" width="{grid_right - label_width}" height="{track_height}" fill="{band_fill}" />'
    )
    track_label_y = current_y + track_height / 2 + 5
    parts.append(f'<text x="24" y="{track_label_y}" class="track-label">{escape(track.name)}</text>')

    for lane_index in range(track.lane_count + 1):
        y = current_y + lane_index * row_height
        parts.append(
            f'<line x1="0" y1="{y}" x2="{grid_right}" y2="{y}" stroke="#ddd3be" stroke-width="1" />'
        )

    for task in track.tasks:
        _render_task(parts, task, current_y, label_width, column_width, row_height)

    return current_y + track_height


def _render_task(
    parts: list[str],
    task: PlacedTask,
    current_y: int,
    label_width: int,
    column_width: int,
    row_height: int,
) -> None:
    x = label_width + task.start * column_width + 6
    width = (task.end - task.start + 1) * column_width - 12
    y = current_y + task.lane * row_height + 6
    height = row_height - 12
    fill = task.color or color_for(task)
    label = escape(task.label)

    parts.append(
        f'<rect x="{x}" y="{y}" width="{width}" height="{height}" rx="7" ry="7" '
        f'fill="{fill}" stroke="#17324d" stroke-opacity="0.15" />'
    )

    if width >= 50:
        parts.append(f'<text x="{x + 10}" y="{y + 17}" class="bar-label" fill="#ffffff">{label}</text>')
    else:
        parts.append(f'<text x="{x + width + 6}" y="{y + 17}" class="bar-label-outside">{label}</text>')


def color_for(task: PlacedTask) -> str:
    index = sum(ord(char) for char in f"{task.track}:{task.label}") % len(PALETTE)
    return PALETTE[index]
