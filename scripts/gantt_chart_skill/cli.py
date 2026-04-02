from __future__ import annotations

import argparse
from pathlib import Path

from .model import count_tasks, detect_lane_collisions, layout_chart, load_chart_spec
from .render import build_ascii_preview, render_svg


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Render a Gantt chart SVG from a JSON timeline spec.")
    parser.add_argument("spec", help="Path to the JSON timeline spec, or '-' to read from stdin")
    parser.add_argument("-o", "--output", default="chart.svg", help="Output SVG path")
    parser.add_argument("--column-width", type=int, help="Width of one timeline column in the SVG")
    parser.add_argument("--day-width", dest="column_width", type=int, help=argparse.SUPPRESS)
    parser.add_argument("--preview", action="store_true", help="Print an ASCII preview to stdout")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        chart = layout_chart(load_chart_spec(args.spec))
    except FileNotFoundError:
        parser.exit(1, f"error: spec file not found: {args.spec}\n")
    except OSError as exc:
        parser.exit(1, f"error: could not read spec {args.spec!r}: {exc}\n")
    except ValueError as exc:
        parser.exit(1, f"error: {exc}\n")

    collisions: list[str] = []
    for track in chart.tracks:
        collisions.extend(detect_lane_collisions(track))

    output_path = Path(args.output)
    try:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(render_svg(chart, column_width=args.column_width), encoding="utf-8")
    except OSError as exc:
        parser.exit(1, f"error: could not write output {args.output!r}: {exc}\n")

    lane_count = sum(track.lane_count for track in chart.tracks)
    print(
        f"Wrote {output_path} | {len(chart.tracks)} tracks | {count_tasks(chart)} tasks | "
        f"{len(chart.axis.keys)} columns | {lane_count} lanes | collisions={len(collisions)}"
    )

    if args.preview:
        print()
        print(build_ascii_preview(chart))

    if collisions:
        for issue in collisions:
            print(issue)
        return 1
    return 0
