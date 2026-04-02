# `gantt-chart`

`gantt-chart` is a standalone Codex skill for creating, revising, and rendering Gantt charts from project notes or JSON timeline specs.

## Install

Clone the repository directly into your Codex skills directory:

```bash
cd ~/.codex/skills
git clone https://github.com/SilverPeak2299/gantt-chart.git
```

This installs the skill at:

```text
~/.codex/skills/gantt-chart
```

Restart Codex after cloning so the skill is loaded.

## Update

Pull the latest changes from GitHub:

```bash
cd ~/.codex/skills/gantt-chart
git pull --ff-only https://github.com/SilverPeak2299/gantt-chart.git main
```

## Use In Codex

Ask Codex to use `$gantt-chart` when you want to:

- turn rough project notes into a chart
- revise an existing Gantt chart spec
- render a JSON timeline file to SVG
- reorganize tasks into tracks, phases, or weekly slots

Example prompts:

```text
Use $gantt-chart to turn these milestones into a Gantt chart.
Use $gantt-chart to update plan.json and render a new SVG.
Use $gantt-chart to convert this roadmap into week-based timeline slots.
```

## Use From The Command Line

Render a spec manually:

```bash
python3 scripts/render_gantt.py path/to/spec.json --output path/to/chart.svg --preview
```

Render from stdin:

```bash
cat path/to/spec.json | python3 scripts/render_gantt.py - --output chart.svg
```

Start from a bundled template:

```bash
cp assets/basic-project.json ./plan.json
python3 scripts/render_gantt.py plan.json --output plan.svg --preview
```

## Note For LLMs And Contributors

This `README.md` is written as user-facing GitHub documentation.
The canonical skill instructions for model behavior live in `SKILL.md`, not here.

## Repository Layout

- `SKILL.md`: model-facing skill trigger and workflow instructions
- `agents/openai.yaml`: skill UI metadata
- `scripts/render_gantt.py`: primary render entrypoint
- `scripts/gantt_chart_skill/`: bundled Python runtime
- `references/`: spec details and examples
- `assets/`: starter chart templates
