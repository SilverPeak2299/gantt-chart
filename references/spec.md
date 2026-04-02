# Spec Format

Use a single JSON object at the top level.

## Common Fields

- `title`: Optional chart title. Defaults to `"Timeline"`.
- `tracks`: Grouped track format.
- `items`: Flat task format.
- `timeline`: Optional custom slot list for weeks, sprints, or phases.

## Grouped Track Format

```json
{
  "title": "Product Launch",
  "tracks": [
    {
      "name": "Engineering",
      "items": [
        { "label": "API", "start": "2026-03-01", "end": "2026-03-05" },
        { "label": "Frontend", "start": "2026-03-03", "end": "2026-03-08" }
      ]
    }
  ]
}
```

## Flat Item Format

```json
{
  "title": "Website Refresh",
  "items": [
    { "label": "Design", "track": "Product", "start": "2026-03-01", "end": "2026-03-03" },
    { "label": "Build", "track": "Engineering", "start": "2026-03-04", "end": "2026-03-10" }
  ]
}
```

## Custom Timeline Format

Use `timeline` when the chart should use named slots instead of dates.

```json
{
  "title": "Quarterly Roadmap",
  "timeline": {
    "title": "Weeks",
    "labels": ["Week 1", "Week 2", "Week 3", "Week 4"]
  },
  "items": [
    { "label": "Prototype", "track": "Design", "start": "Week 1", "end": "Week 2" },
    { "label": "Build", "track": "Engineering", "start": "Week 2", "end": "Week 4" }
  ]
}
```

## Task Rules

- Each task needs `label` or `name`.
- Each task needs both `start` and `end`.
- Date timelines require ISO dates in `YYYY-MM-DD`.
- Custom timelines require `start` and `end` values that match a label in `timeline.labels`.
- Dates are inclusive.
- Tasks inside one track can overlap; the renderer will assign separate lanes.
- Optional `color` accepts any SVG/CSS color string.

## Validation Notes

- `tracks` must be a non-empty list when used.
- `items` must be a non-empty list when used.
- `timeline.labels` must be unique and non-empty.
- `end` cannot come before `start`.
