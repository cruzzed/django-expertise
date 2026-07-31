# Recipe: sticky form save indicator (autosave)

- **ID:** `hyperscript-recipe-autosave`
- **Category:** hyperscript
- **Source:** §5.3 Recipe: Sticky form save indicator
- **Tags:** `hyperscript`, `autosave`, `htmx-events`

## Canonical pattern (Django / HTMX / Hyperscript way)
Form with hx-trigger='keyup changed delay:1s from :is(input, textarea, select)' autosaves any field; hyperscript listens on htmx:beforeRequest to show 'Saving...' and htmx:afterRequest to show success/failure with conditional class changes using event.detail.successful.

## Laravel / MVC default (what AI typically generates)
AI implements a useEffect debounce per field in React with a global saving boolean in state, or jQuery .on('input') + setTimeout chains per form, duplicating the status-label logic each time.

## Why Django differs
The declarative hx-trigger from: modifier autosaves the whole form with one attribute; hyperscript reads event.detail.successful directly for the status branch. Behavior identical to the Phase-1 hx-on version, but declarative - per the two-phase workflow.

## Example
<form id="editor" hx-post="{% url 'autosave' %}"
      hx-trigger="keyup changed delay:1s from :is(input, textarea, select)"
      _="on htmx:beforeRequest
           put 'Saving...' into #save-status
         end
         on htmx:afterRequest
           if event.detail.successful
             put 'All changes saved' into #save-status
           else
             put 'Save failed!' into #save-status
             add .text-error to #save-status
           end
         end">
  <span id="save-status">All changes saved</span>
</form>
