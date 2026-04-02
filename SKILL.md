---
name: gantt-chart
description: Create, revise, and render Gantt charts from rough project plans, milestone lists, schedule notes, or timeline JSON. Use when Codex needs to turn planning input into a clear Gantt chart, update an existing chart spec, rebalance tracks or dates, or produce SVG output for delivery.
---

# Gantt Chart

Turn rough planning input or existing timeline JSON into a rendered SVG Gantt chart.
Prefer editing an existing spec in the workspace. If no spec exists, copy a starter file from `assets/` into the workspace and edit that copy instead of writing into the installed skill checkout.

## Workflow

1. Normalize the user's input into a JSON spec.
   - If the user provides prose, turn it into explicit tasks with `label`, `start`, `end`, and either grouped `tracks` or flat `items`.
   - If the user already has a JSON file, update that file in place when possible.
2. Validate the spec before rendering.
   - Keep `start` and `end` inclusive.
   - Use ISO dates like `2026-04-01` for date-based timelines.
   - Use a custom `timeline` only when the chart should use named slots such as weeks, sprints, or phases.
3. Render the chart with the bundled script.

```bash
python3 scripts/render_gantt.py path/to/spec.json --output path/to/chart.svg --preview
```

4. Write outputs into the user's workspace.
   - Default to a relative output path such as `chart.svg`.
   - Do not write rendered charts back into the skill directory unless the user explicitly asks.

## Spec Guidance

- Use grouped `tracks` when the user already thinks in swimlanes such as Design, Engineering, and Launch.
- Use flat `items` with `track` when building a spec from mixed notes and then let the renderer group them.
- Add `color` only when the user requests fixed colors or category coding.
- Use `timeline.title` and `timeline.labels` for week-by-week or phase-based plans.

Read [references/spec.md](references/spec.md) for the accepted schema and validation rules.
Read [references/examples.md](references/examples.md) for common patterns and commands.

## Resources

### scripts/

- `scripts/render_gantt.py`: Render a JSON spec to SVG and optionally print an ASCII preview.

### references/

- `references/spec.md`: Field-level schema and rules.
- `references/examples.md`: Working command examples and planning patterns.

### assets/

- `assets/basic-project.json`: Starter template for a date-based project plan.
- `assets/weekly-roadmap.json`: Starter template for a week-slot roadmap.
