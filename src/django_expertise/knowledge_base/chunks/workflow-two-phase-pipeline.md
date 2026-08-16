# Two-phase interactivity pipeline (htmx-writer -> spa-evolver)

- **ID:** `workflow-two-phase-pipeline`
- **Category:** workflow
- **Source:** §6 Workflow, §2.3, §2.4
- **Tags:** `workflow`, `hx-on`, `hyperscript`, `translation`

## Canonical pattern (Django / HTMX / Hyperscript way)
Phase 1 (htmx-writer): implement interactivity with hx-on:* attributes containing working vanilla JS, add HYPERSCRIPT-TODO comments, and validate behavior. Phase 2 (spa-evolver): translate each hx-on handler into declarative _hyperscript, verify identical behavior, remove all hx-on attributes, add TRANSLATED-BY comment. Failed validation at either gate returns work to the responsible persona.

## Typical MVC default (what AI typically generates)
AI jumps straight to a JS framework or writes inline <script> tags and imperative DOM spaghetti in one pass, with no separation between 'make it work' and 'make it clean', and no verification step between iterations.

## Why Django differs
Splitting prototype-then-refine mirrors how HTMX apps should evolve: get behavior right with familiar vanilla JS, then gain hyperscript's declarative locality. The validation gates guarantee Phase 2 is a behavior-preserving refactor, not a rewrite.

## Example
<!-- Phase 1 output (htmx-writer) -->
<!-- HYPERSCRIPT-TODO: show success message 2s then clear; handle error state -->
<button hx-post="/api/action/" hx-target="#result"
        hx-on:htmx:after-request="
          if (event.detail.successful) {
            this.textContent = 'Saved!';
            setTimeout(() => this.textContent = 'Submit', 2000);
          }">Submit</button>

<!-- Phase 2 output (spa-evolver) -->
<!-- TRANSLATED-BY: spa-evolver -->
<button hx-post="/api/action/" hx-target="#result"
        _="on htmx:afterRequest
             if event.detail.successful
               put 'Saved!' into me
               wait 2s
               put 'Submit' into me
             end
           end">Submit</button>
