# Examples

Use the bundled templates as starting points:

- `assets/basic-project.json`: Date-based project plan.
- `assets/weekly-roadmap.json`: Week-slot roadmap.

## Common Commands

Render a workspace file to SVG:

```bash
python3 scripts/render_gantt.py plan.json --output plan.svg --preview
```

Render from stdin:

```bash
cat plan.json | python3 scripts/render_gantt.py - --output plan.svg
```

Render into a nested output directory:

```bash
python3 scripts/render_gantt.py plan.json --output build/charts/plan.svg
```

## Planning Patterns

- Use date-based timelines for delivery schedules with real calendar dates.
- Use a custom `timeline.labels` list for sprint plans, phased rollouts, or fixed weekly slots.
- Split tracks by function when the chart should show ownership.
- Keep labels short when many tasks share the same track.
- Add explicit colors only when the chart needs a legend or category meaning.
