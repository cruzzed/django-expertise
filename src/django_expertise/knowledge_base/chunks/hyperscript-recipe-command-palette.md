# Recipe: Ctrl+K command palette

- **ID:** `hyperscript-recipe-command-palette`
- **Category:** hyperscript
- **Source:** §5.3 Recipe: Command palette
- **Tags:** `hyperscript`, `keyboard`, `modal`

## Canonical pattern (Django / HTMX / Hyperscript way)
Global keydown filter syntax: on keydown[key is 'k' and ctrlKey] halt the event, reveal #command-palette, focus() the input. Inside, an hx-get search input (delay:100ms) renders results; Escape on the input hides the modal via closest .modal.

## Typical MVC default (what AI typically generates)
AI builds a SPA modal portal with a global keydown listener in an effect hook, focus trapping via refs, and a fetch-driven results list - or installs a command-palette dependency.

## Why Django differs
Hyperscript's event-filter bracket syntax expresses chorded shortcuts inline; focus() and hidden-class toggling replace the modal-state machinery. Server-rendered results via hx-get mean the palette needs no client-side search index.

## Example
<body _="on keydown[key is 'k' and ctrlKey]
    halt the event
    remove .hidden from #command-palette
    focus() on #command-input
  end">

<div id="command-palette" class="hidden modal"
     _="on click if event.target is me add .hidden to me end end">
  <input id="command-input" type="text" placeholder="Type a command..."
         hx-get="{% url 'command-search' %}" hx-target="#command-results"
         hx-trigger="keyup changed delay:100ms"
         _="on keydown[key is 'Escape'] add .hidden to closest .modal end">
  <div id="command-results"></div>
</div>
