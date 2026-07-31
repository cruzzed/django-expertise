# Recipes: exclusive accordion and character counter

- **ID:** `hyperscript-recipe-accordion-counter`
- **Category:** hyperscript
- **Source:** §5.3 Common Hyperscript Recipes
- **Tags:** `hyperscript`, `accordion`, `counter`, `tell`

## Canonical pattern (Django / HTMX / Hyperscript way)
Accordion: on click, tell the details in the closest <.accordion/> to set its open to false for siblings (if it is not me). Counter: on input compute remaining from my value's length, put it into #char-count, and toggle a warning class when under threshold.

## Laravel / MVC default (what AI typically generates)
AI uses a jQuery accordion plugin / Bootstrap collapse JS, and for counters a keyup handler with $('#count').text(500 - this.value.length) plus manual class toggling in a script block.

## Why Django differs
Hyperscript's tell command addresses sibling elements with natural CSS-ish selectors from the element itself - no global document.querySelector wiring. if/else with add/remove of classes keeps the state logic next to the element it affects.

## Example
<details _="on click
    tell the details in the closest <.accordion/>
      if it is not me
        set its open to false
      end
    end">
  <summary>{{ faq.question }}</summary><p>{{ faq.answer }}</p>
</details>

<textarea name="description" maxlength="500"
  _="on input
    set :remaining to 500 - my value's length
    put :remaining into #char-count
    if :remaining < 50
      add .text-warning to #char-count
    else
      remove .text-warning from #char-count
    end"></textarea>
<span id="char-count">500</span> characters remaining
