# django-expertise

A reusable toolkit for Django + HTMX + Hyperscript projects. It bundles an anti-pattern sentinel, two-phase interactivity router, Kimi Code persona prompts, and a structured Django knowledge base into an installable Python package.

## Install

```bash
pip install kimi-django-expertise
```

Or with `uv`:

```bash
uv add --dev kimi-django-expertise
```

## Commands

```bash
# Scan a project for anti-patterns A-001..A-015
django-expertise-sentinel .

# Route a task description to the right persona
django-expertise-router route "add live search to the product list"

# Validate Phase 1 / Phase 2 handoff
django-expertise-router validate-phase1 my_template.html
django-expertise-router validate-phase2 my_template.html
django-expertise-router handoff my_template.html

# Install Kimi Code skills/agents into the current project or user directory
django-expertise install --target project
django-expertise install --target user
django-expertise install --target project --force

# Inspect the bundled knowledge base
django-expertise kb list
django-expertise kb show anti-a001-signals-business-logic
django-expertise kb index
```

## Project configuration

Add a `[tool.django-expertise]` section to your project's `pyproject.toml`:

```toml
[tool.django-expertise]
skip_dirs = [".git", ".venv", "__pycache__", "node_modules"]
skip_paths = ["explore_legacy.py"]

[tool.django-expertise.per_rule_skip_paths]
A-006 = ["myapp/management/commands/import_legacy.py"]
A-013 = ["myapp/htmx_only_views.py"]
```

## What's included

- `django_expertise.sentinel` — static anti-pattern scanner for Python, HTML, and JS.
- `django_expertise.router` + `django_expertise.gates` — two-phase interactivity router and quality gates.
- `django_expertise.kimi.skills` and `django_expertise.kimi.agents` — Kimi Code persona files.
- `django_expertise.knowledge_base` — bundled knowledge base with 68 chunks covering Django core, contrib modules, HTMX, Hyperscript, anti-patterns, and workflow handoffs.

## Development

```bash
uv pip install -e ".[dev]"
pytest
```

## Publishing

This package uses PyPI trusted publishing. Push a tag and the GitHub Actions release workflow builds and uploads the wheel/sdist:

```bash
git tag v0.1.3
git push origin v0.1.3
```

## License

MIT
