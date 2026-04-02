from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, timedelta
import json
from pathlib import Path
import sys
from typing import Any

SYMBOLS = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"


@dataclass
class TimelineAxis:
    kind: str
    keys: list[str]
    title: str = "Timeline"
    subtitle: str = ""
    _index_by_key: dict[str, int] = field(init=False, repr=False)

    def __post_init__(self) -> None:
        normalized = [str(key).strip() for key in self.keys]
        if not normalized:
            raise ValueError("Timeline must contain at least one time slot")
        if len(set(normalized)) != len(normalized):
            raise ValueError("Timeline keys must be unique")
        self.keys = normalized
        self._index_by_key = {key: index for index, key in enumerate(self.keys)}
        if not self.subtitle:
            self.subtitle = f"{self.keys[0]} to {self.keys[-1]}"

    def index_of(self, key: str) -> int:
        try:
            return self._index_by_key[key]
        except KeyError as exc:
            raise ValueError(f"Unknown timeline slot: {key!r}") from exc


@dataclass(frozen=True)
class Task:
    label: str
    start: int
    end: int
    track: str
    color: str | None = None
    start_key: str = ""
    end_key: str = ""


@dataclass(frozen=True)
class PlacedTask(Task):
    lane: int = 0
    symbol: str = "?"


@dataclass
class Track:
    name: str
    tasks: list[Task] = field(default_factory=list)


@dataclass
class PlacedTrack:
    name: str
    tasks: list[PlacedTask]
    lane_count: int


@dataclass
class Chart:
    title: str
    axis: TimelineAxis
    tracks: list[Track]


@dataclass
class PlacedChart:
    title: str
    axis: TimelineAxis
    tracks: list[PlacedTrack]


def parse_date(value: str) -> date:
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise ValueError(f"Invalid ISO date: {value!r}") from exc


def load_chart_spec(path: str | Path) -> Chart:
    raw = json.loads(read_spec_text(path))
    if not isinstance(raw, dict):
        raise ValueError("Top-level spec must be a JSON object")
    return chart_from_dict(raw)


def read_spec_text(path: str | Path) -> str:
    if str(path) == "-":
        contents = sys.stdin.read()
        if not contents.strip():
            raise ValueError("No JSON was provided on stdin")
        return contents
    return Path(path).read_text(encoding="utf-8")


def chart_from_dict(raw: dict[str, Any]) -> Chart:
    title = str(raw.get("title") or "Timeline")
    raw_tracks = collect_raw_tracks(raw)
    axis = build_axis(raw, raw_tracks)
    tracks = [
        Track(name=track_name, tasks=[task_from_dict(item, track_name, axis) for item in raw_items])
        for track_name, raw_items in raw_tracks
    ]
    return Chart(title=title, axis=axis, tracks=tracks)


def collect_raw_tracks(raw: dict[str, Any]) -> list[tuple[str, list[dict[str, Any]]]]:
    tracks: list[tuple[str, list[dict[str, Any]]]] = []
    raw_tracks = raw.get("tracks")

    if raw_tracks is not None:
        if not isinstance(raw_tracks, list) or not raw_tracks:
            raise ValueError("'tracks' must be a non-empty list")
        for raw_track in raw_tracks:
            if not isinstance(raw_track, dict):
                raise ValueError("Each track must be an object")
            name = str(raw_track.get("name") or raw_track.get("label") or "Timeline")
            items = raw_track.get("items") or raw_track.get("tasks")
            if not isinstance(items, list) or not items:
                raise ValueError(f"Track {name!r} must contain a non-empty 'items' list")
            typed_items: list[dict[str, Any]] = []
            for item in items:
                if not isinstance(item, dict):
                    raise ValueError("Each item must be an object")
                typed_items.append(item)
            tracks.append((name, typed_items))
    else:
        items = raw.get("items") or raw.get("tasks")
        if not isinstance(items, list) or not items:
            raise ValueError("Spec must define either 'tracks' or a non-empty 'items' list")
        grouped: dict[str, list[dict[str, Any]]] = {}
        order: list[str] = []
        for item in items:
            if not isinstance(item, dict):
                raise ValueError("Each item must be an object")
            track_name = str(item.get("track") or "Timeline")
            if track_name not in grouped:
                grouped[track_name] = []
                order.append(track_name)
            grouped[track_name].append(item)
        tracks = [(name, grouped[name]) for name in order]

    if not tracks:
        raise ValueError("Spec did not contain any tasks")
    return tracks


def build_axis(raw: dict[str, Any], raw_tracks: list[tuple[str, list[dict[str, Any]]]]) -> TimelineAxis:
    raw_timeline = raw.get("timeline")
    if raw_timeline is None:
        return build_date_axis(raw_tracks)
    return build_tag_axis(raw_timeline, raw.get("timeline_title"))


def build_tag_axis(raw_timeline: Any, fallback_title: Any) -> TimelineAxis:
    axis_title = "Timeline"
    labels: list[str]

    if isinstance(raw_timeline, dict):
        raw_labels = raw_timeline.get("labels") or raw_timeline.get("slots")
        axis_title = str(raw_timeline.get("title") or fallback_title or "Timeline")
    else:
        raw_labels = raw_timeline
        axis_title = str(fallback_title or "Timeline")

    if not isinstance(raw_labels, list) or not raw_labels:
        raise ValueError("'timeline' must be a non-empty list or an object with a non-empty 'labels' list")

    labels = [str(label).strip() for label in raw_labels]
    return TimelineAxis(kind="tag", keys=labels, title=axis_title)


def build_date_axis(raw_tracks: list[tuple[str, list[dict[str, Any]]]]) -> TimelineAxis:
    starts: list[date] = []
    ends: list[date] = []
    for _, items in raw_tracks:
        for item in items:
            starts.append(parse_date(str(item.get("start"))))
            ends.append(parse_date(str(item.get("end"))))

    if not starts or not ends:
        raise ValueError("Spec did not contain any tasks")

    first_day = min(starts)
    last_day = max(ends)
    day_count = (last_day - first_day).days + 1
    labels = [(first_day + timedelta(days=index)).isoformat() for index in range(day_count)]
    return TimelineAxis(kind="date", keys=labels, title="Dates", subtitle=f"{labels[0]} to {labels[-1]}")


def task_from_dict(raw: dict[str, Any], fallback_track: str, axis: TimelineAxis) -> Task:
    label = raw.get("label") or raw.get("name")
    if not label:
        raise ValueError("Each task needs 'label' or 'name'")

    start_value = raw.get("start")
    end_value = raw.get("end")
    if start_value is None or end_value is None:
        raise ValueError(f"Task {label!r} needs both 'start' and 'end'")

    start_key = normalize_time_key(start_value, axis.kind)
    end_key = normalize_time_key(end_value, axis.kind)
    start_index = axis.index_of(start_key)
    end_index = axis.index_of(end_key)
    if end_index < start_index:
        raise ValueError(f"Task {label!r} ends before it starts")

    color = raw.get("color")
    if color is not None:
        color = str(color)
    track = str(raw.get("track") or fallback_track)

    return Task(
        label=str(label),
        start=start_index,
        end=end_index,
        track=track,
        color=color,
        start_key=start_key,
        end_key=end_key,
    )


def normalize_time_key(value: Any, axis_kind: str) -> str:
    if axis_kind == "date":
        return parse_date(str(value)).isoformat()
    return str(value).strip()


def layout_chart(chart: Chart) -> PlacedChart:
    placed_tracks: list[PlacedTrack] = []
    for track in chart.tracks:
        placed_tasks, lane_count = assign_lanes(track.tasks)
        placed_tracks.append(PlacedTrack(name=track.name, tasks=placed_tasks, lane_count=lane_count))
    return PlacedChart(title=chart.title, axis=chart.axis, tracks=placed_tracks)


def assign_lanes(tasks: list[Task]) -> tuple[list[PlacedTask], int]:
    ordered = sorted(tasks, key=lambda task: (task.start, task.end, task.label))
    lane_ends: list[int] = []
    placed: list[PlacedTask] = []

    for index, task in enumerate(ordered):
        lane_index = find_open_lane(lane_ends, task.start)
        if lane_index is None:
            lane_index = len(lane_ends)
            lane_ends.append(task.end)
        else:
            lane_ends[lane_index] = task.end

        placed.append(
            PlacedTask(
                label=task.label,
                start=task.start,
                end=task.end,
                track=task.track,
                color=task.color,
                start_key=task.start_key,
                end_key=task.end_key,
                lane=lane_index,
                symbol=_symbol_for(index),
            )
        )

    return placed, max(1, len(lane_ends))


def find_open_lane(lane_ends: list[int], start: int) -> int | None:
    for index, lane_end in enumerate(lane_ends):
        if start > lane_end:
            return index
    return None


def detect_lane_collisions(track: PlacedTrack) -> list[str]:
    issues: list[str] = []
    by_lane: dict[int, list[PlacedTask]] = {}
    for task in track.tasks:
        by_lane.setdefault(task.lane, []).append(task)

    for lane, lane_tasks in by_lane.items():
        ordered = sorted(lane_tasks, key=lambda task: (task.start, task.end, task.label))
        previous: PlacedTask | None = None
        for task in ordered:
            if previous is not None and task.start <= previous.end:
                issues.append(
                    f"Track {track.name!r} lane {lane} overlaps: {previous.label!r} and {task.label!r}"
                )
            previous = task

    return issues


def count_tasks(chart: PlacedChart) -> int:
    return sum(len(track.tasks) for track in chart.tracks)


def _symbol_for(index: int) -> str:
    if index < len(SYMBOLS):
        return SYMBOLS[index]
    return "*"
