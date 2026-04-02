# `gantt-chart`

Standalone Codex skill for creating, updating, and rendering Gantt charts from JSON timeline specs.

## Install

From the machine where Codex runs, go to your skills directory and clone the repo:

```bash
cd ~/.codex/skills
git clone https://github.com/<your-github-username>/gantt-chart.git
```

That creates the expected install path:

```text
~/.codex/skills/gantt-chart
```

Restart Codex after installing so the new skill is picked up.

## Update

```bash
cd ~/.codex/skills/gantt-chart
git pull --ff-only
```

## Use

Ask Codex to use `$gantt-chart` to build or revise a chart from project notes or a JSON spec.

Render a spec manually:

```bash
python3 scripts/render_gantt.py path/to/spec.json --output path/to/chart.svg --preview
```

Use one of the bundled starter templates:

```bash
cp assets/basic-project.json ./plan.json
python3 scripts/render_gantt.py plan.json --output plan.svg --preview
```

## Repository Layout

- `SKILL.md`: skill trigger and workflow instructions
- `agents/openai.yaml`: UI metadata
- `scripts/render_gantt.py`: main render entrypoint
- `scripts/gantt_chart_skill/`: bundled Python runtime
- `references/`: JSON spec docs and examples
- `assets/`: starter templates
