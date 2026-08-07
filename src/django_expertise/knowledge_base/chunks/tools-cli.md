# django-expertise CLI usage manual

This document describes the command-line tools shipped with `django-expertise`. Agents should consult this manual before using the toolkit so they invoke the right command for the right job.

## Installation

```bash
pip install --pre kimi-django-expertise
```

Optional extras:

```bash
pip install --pre "kimi-django-expertise[browser]"   # Playwright browser tools
pip install --pre "kimi-django-expertise[mcp]"       # MCP server
```

## Entry points

| Command | Purpose |
|---|---|
| `django-expertise` | Main toolkit: install, KB, debug, browser, setup-dev, MCP server |
| `django-expertise-sentinel` | Standalone anti-pattern scanner |
| `django-expertise-router` | Standalone two-phase interactivity router |
| `django-expertise-mcp` | Standalone MCP server (requires `[mcp]` extra) |

## `django-expertise install`

Install Kimi Code skills, agents, and knowledge base into the current project or user directory.

```bash
django-expertise install --target project
django-expertise install --target user
django-expertise install --target project --skip-existing
```

After installing, add this line to your project's `AGENTS.md`:

> Always read `.kimi-code/knowledge-base/chunks/tools-cli.md` for using `django-expertise` tooling.

## `django-expertise kb`

Inspect the bundled knowledge base.

```bash
django-expertise kb list          # list chunks by category
django-expertise kb show <id>     # show a chunk
django-expertise kb index         # dump chunks.jsonl
django-expertise kb path          # print package path
```

## `django-expertise debug`

Agent-friendly debugging wrappers. Requires a Django project with `DJANGO_SETTINGS_MODULE` set.

### `debug test`

Run a test with agent-friendly output.

```bash
django-expertise debug test sales.tests.test_checkout --pdb --sql
django-expertise debug test myapp.tests --no-verbose --extra-args --tb=short
```

Flags:
- `--pdb` — drop into the debugger on failure
- `--sql` — log SQL queries
- `--no-verbose` — disable verbose output
- `--extra-args` — pass remaining arguments to the test runner

### `debug runserver`

Run the Django dev server with optional debug helpers.

```bash
django-expertise debug runserver --toolbar
django-expertise debug runserver 0.0.0.0:8000 --silk
```

Flags:
- `--toolbar` — verify `django-debug-toolbar` is available
- `--silk` — verify `django-silk` is available

### `debug probe`

Insert or remove temporary debug probes into functions at runtime.

```bash
django-expertise debug probe insert sales.views.checkout#process_payment --type print
django-expertise debug probe insert sales.views.checkout#process_payment --type breakpoint
django-expertise debug probe remove sales.views.checkout#process_payment
django-expertise debug probe list
```

Probe types:
- `print` — log entry/exit and arguments
- `breakpoint` — pause execution (uses `ipdb` if available)

### `debug analyze-request`

Analyze a Django HTTP response for HTMX headers, SQL, templates, and timing.

```bash
django-expertise debug analyze-request /sales/checkout/ --htmx
```

### `debug last-request`

Print the last captured MVT observation as JSON. Requires either `DJANGO_SETTINGS_MODULE` (direct call) or a running dev server (HTTP mode).

```bash
# Direct mode
cd myproject && DJANGO_SETTINGS_MODULE=myproject.settings django-expertise debug last-request

# HTTP mode
django-expertise debug last-request --host 127.0.0.1 --port 8000
```

The observation includes request/response metadata, SQL queries, rendered templates, FormView state, `form.errors`, and rendered error counts.

## `django-expertise browser`

Browser automation for HTMX/Hyperscript verification. Requires the `[browser]` extra (`playwright`).

### `browser console`

Capture browser console logs for a URL.

```bash
django-expertise browser console --url http://localhost:8000/sales/checkout --click "#submit"
```

### `browser snapshot`

Capture rendered HTML.

```bash
django-expertise browser snapshot --url http://localhost:8000/sales/checkout
```

### `browser htmx-trace`

Trace an HTMX request/response cycle.

```bash
django-expertise browser htmx-trace --url http://localhost:8000/sales/checkout --selector "#save-btn"
```

## `django-expertise setup-devuser`

Create a local dev superuser non-interactively.

```bash
django-expertise setup-devuser --username admin --email admin@example.com --password admin --dev-mode
```

## `django-expertise seed-fixtures`

Load or scaffold fixture data.

```bash
django-expertise seed-fixtures myapp --fixture fixtures/initial.json
django-expertise seed-fixtures myapp --generate-template
```

## `django-expertise mcp`

Start the `django-expertise` MCP server. Requires the `[mcp]` extra.

```bash
django-expertise mcp --transport stdio
django-expertise mcp --transport sse --port 8001
```

MCP tools include `sentinel_scan`, `router_route`, `debug_probe_insert`, `debug_probe_remove`, `browser_snapshot`, `browser_htmx_trace`, `setup_devuser`, and `seed_fixtures`.

## `django-expertise-sentinel`

Scan a project for anti-patterns A-001..A-015.

```bash
django-expertise-sentinel .
django-expertise-sentinel src/ templates/
```

Configuration is read from `[tool.django-expertise]` in `pyproject.toml`.

## `django-expertise-router`

Route a task to the right persona or validate phase gates.

```bash
django-expertise-router route "add live search to the product list"
django-expertise-router validate-phase1 my_template.html
django-expertise-router validate-phase2 my_template.html
django-expertise-router handoff my_template.html
```

## Skill precedence

When using `django-expertise` alongside generic autonomous-execution plugins (e.g. Superpowers), `django-expertise` roles and conventions take precedence for Django + HTMX + Hyperscript work. Generic plugins may handle workflow mechanics (todos, worktrees, reviews), but they must not override role-based delegation, the anti-pattern registry, or the design-gate / implementation-gate separation.
