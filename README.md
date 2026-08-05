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
# (overwrites existing files by default; use --skip-existing to leave them alone)
django-expertise install --target project
django-expertise install --target user
django-expertise install --target project --skip-existing

# Inspect the bundled knowledge base
django-expertise kb list
django-expertise kb show anti-a001-signals-business-logic
django-expertise kb index

# Debug backend code (wrappers around pytest, runserver, pdb)
django-expertise debug test sales.tests.test_checkout --sql
django-expertise debug runserver --toolbar
django-expertise debug probe insert sales.views.checkout#process_payment
django-expertise debug probe remove sales.views.checkout#process_payment
django-expertise debug analyze-request /sales/checkout/ --htmx

# Verify HTMX/Hyperscript behavior in a real browser
django-expertise browser console --url http://localhost:8000/sales/checkout --click "#submit"
django-expertise browser snapshot --url http://localhost:8000/sales/checkout
django-expertise browser htmx-trace --url http://localhost:8000/sales/checkout --selector "#save-btn"

# Set up a local dev environment
django-expertise setup-devuser --username admin --password admin --email admin@example.local --dev-mode
django-expertise seed-fixtures sales
```

Browser automation requires the `[browser]` extra: `pip install kimi-django-expertise[browser]`.

The MCP server requires the `[mcp]` extra: `pip install kimi-django-expertise[mcp]`, then register it in your agent:

```json
{
  "mcpServers": {
    "django-expertise": {
      "command": "django-expertise-mcp",
      "args": []
    }
  }
}
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

## Recommended companion tooling for agent-driven development

`django-expertise` focuses on guidance, quality gates, and HTMX/Hyperscript-specific verification. For general Django introspection and debugging, install these companions instead of reinventing them:

| Concern | Recommended tool | Why |
|---|---|---|
| Models, schema, URLs, settings, read-only ORM queries | [`django-ai-boost`](https://github.com/vintasoftware/django-ai-boost) | MCP server inspired by Laravel Boost |
| Request/response SQL, templates, cache, signals | [`django-debug-toolbar`](https://django-debug-toolbar.readthedocs.io/) or [`django-silk`](https://github.com/jazzband/django-silk) | Mature request introspection |
| Interactive debugging | `pdb`, [`ipdb`](https://github.com/gotcha/ipdb), or [`debugpy`](https://github.com/microsoft/debugpy) | Standard Python debuggers |
| Testing | [`pytest`](https://docs.pytest.org/) + [`pytest-django`](https://pytest-django.readthedocs.io/) | Standard test runner |
| Browser automation, console logs, screenshots | [Playwright](https://playwright.dev/) or [Playwright MCP](https://github.com/microsoft/playwright-mcp) | Agent-friendly browser control |

`django-expertise` provides thin wrappers and HTMX-specific helpers on top of these tools rather than replacing them.

## Development

```bash
uv pip install -e ".[dev]"
pytest
```

## Publishing

This package uses PyPI trusted publishing. Push a tag and the GitHub Actions release workflow builds and uploads the wheel/sdist:

```bash
git tag v0.1.5
git push origin v0.1.5
```

## Skill precedence when mixing with other plugins

Based on real usage by the creator, depending on your needs you may need to strictly and explicitly state a precedence for skill-usage priority when using other project-based skills that have mandates of their own. For example:

> For Django + HTMX + Hyperscript work, `django-expertise` roles take precedence over generic autonomous-execution plugins such as Superpowers. Superpowers skills may be used for workflow mechanics (todos, worktrees, reviews), but they may not override the role-based delegation defined by `django-expertise`, the anti-pattern registry (A-001..A-015), or the design-gate / implementation-gate separation.

## License

MIT
