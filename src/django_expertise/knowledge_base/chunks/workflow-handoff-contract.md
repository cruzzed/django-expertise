# Handoff contract and translation rules

- **ID:** `workflow-handoff-contract`
- **Category:** workflow
- **Source:** §6.1 Handoff Contract, §2.4 Translation Rules
- **Tags:** `workflow`, `handoff`, `hyperscript`, `translation-rules`

## Canonical pattern (Django / HTMX / Hyperscript way)
HYPERSCRIPT-TODO comments specify Event, Action, State, Edge cases, Notes. Translation table: classList.add -> add .x to me; textContent= -> put 'y' into #x; setTimeout(fn,2000) -> wait 2s; preventDefault -> halt the event; htmx.trigger(el,'e') -> trigger e on el. Advanced features: tell, transition, make a <div/>, repeat for, measure, fetch. Output gets a TRANSLATED-BY comment listing features used.

## Typical MVC default (what AI typically generates)
AI rewrites handlers ad hoc with no spec comment, mixes hx-on and _ attributes on the same element, and 'improves' behavior during translation - breaking parity with the validated Phase-1 version.

## Why Django differs
The contract makes handoffs machine-checkable: the TODO comment is the spec, the table is the mapping, and the TRANSLATED-BY comment is the audit trail. Behavioral identity (not improvement) is the Phase-2 acceptance criterion per quality gate 4.

## Example
<!-- HANDOFF TEMPLATE -->
<!--
  HYPERSCRIPT-TODO:
  - Event: htmx:afterRequest on this element
  - Action: Show success message for 2s, then clear
  - State: Track original button text in :original variable
  - Edge case: Handle both success and error states
  - Notes: The success message should fade in/out smoothly
-->

<!-- Keyboard shortcut example of advanced syntax -->
<body _="on keydown[key is 's' and ctrlKey]
    halt the event
    trigger submit on <form#quick-save/>
  end">
