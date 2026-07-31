# K3 Swarm Knowledge Base Index

Total chunks: 68


## django-core (17)

| ID | Title | Source |
|----|-------|--------|
| [core-model-queryset-manager](chunks/core-model-queryset-manager.md) | models.Model, QuerySet, and custom Managers | §3.1 Core Framework |
| [core-select-prefetch-related](chunks/core-select-prefetch-related.md) | select_related() and prefetch_related() | §3.1 Core Framework |
| [core-annotate-aggregate](chunks/core-annotate-aggregate.md) | annotate() vs aggregate() | §3.1 Core Framework |
| [core-f-expressions](chunks/core-f-expressions.md) | F() expressions for database-level operations | §3.1 Core Framework |
| [core-q-objects](chunks/core-q-objects.md) | Q() objects for complex lookups | §3.1 Core Framework |
| [core-subquery-window](chunks/core-subquery-window.md) | Subquery/OuterRef and Window functions | §3.1 Core Framework |
| [core-custom-user-model](chunks/core-custom-user-model.md) | get_user_model(), AbstractUser, AbstractBaseUser | §3.1 Core Framework |
| [core-auth-permissions-groups](chunks/core-auth-permissions-groups.md) | Permission and Group (RBAC primitives) | §3.1 Core Framework |
| [core-auth-mixins-decorators](chunks/core-auth-mixins-decorators.md) | login_required and CBV access mixins | §3.1 Core Framework |
| [core-forms-modelform](chunks/core-forms-modelform.md) | django.forms Form and ModelForm | §3.1 Core Framework |
| [core-cbv-editing](chunks/core-cbv-editing.md) | Editing CBVs: FormView, CreateView, UpdateView, DeleteView | §3.1 Core Framework, §2.2 CBV Decision Matrix |
| [core-cbv-display](chunks/core-cbv-display.md) | Display CBVs: ListView, DetailView, TemplateView, RedirectView | §3.1 Core Framework, §2.2 CBV Decision Matrix |
| [core-dispatch-shortcuts](chunks/core-dispatch-shortcuts.md) | View.dispatch() and django.shortcuts helpers | §3.1 Core Framework, §2.2 View Layer |
| [core-url-routing](chunks/core-url-routing.md) | path(), re_path(), include(), reverse(), resolve() | §3.1 Core Framework |
| [core-middleware-hooks](chunks/core-middleware-hooks.md) | Middleware: MiddlewareMixin, process_view, process_template_response | §3.1 Core Framework, §4.3 |
| [core-caching-memoization](chunks/core-caching-memoization.md) | Caching: cache_page, cached_property, lru_cache | §3.1 Core Framework |
| [core-settings-appconfig](chunks/core-settings-appconfig.md) | settings access and AppConfig.ready() | §3.1 Core Framework |

## contrib (11)

| ID | Title | Source |
|----|-------|--------|
| [contrib-admin](chunks/contrib-admin.md) | django.contrib.admin and ModelAdmin | §3.2 Contrib Modules, A-005 |
| [contrib-auth](chunks/contrib-auth.md) | django.contrib.auth (full authentication stack) | §3.2 Contrib Modules, §2.1 Decision Tree |
| [contrib-contenttypes](chunks/contrib-contenttypes.md) | django.contrib.contenttypes (GenericForeignKey) | §3.2 Contrib Modules, A-015 |
| [contrib-sessions](chunks/contrib-sessions.md) | django.contrib.sessions (server-side sessions) | §3.2 Contrib Modules, A-011 |
| [contrib-messages](chunks/contrib-messages.md) | django.contrib.messages (flash messages) | §3.2 Contrib Modules, §4.2 OOB Toast |
| [contrib-staticfiles](chunks/contrib-staticfiles.md) | django.contrib.staticfiles | §3.2 Contrib Modules, §5.1 |
| [contrib-humanize](chunks/contrib-humanize.md) | django.contrib.humanize (natural-language template filters) | §3.2 Contrib Modules |
| [contrib-sitemaps-syndication](chunks/contrib-sitemaps-syndication.md) | django.contrib.sitemaps and django.contrib.syndication | §3.2 Contrib Modules, §2.1 Decision Tree |
| [contrib-postgres](chunks/contrib-postgres.md) | django.contrib.postgres (PostgreSQL-specific fields/search) | §3.2 Contrib Modules |
| [contrib-gis](chunks/contrib-gis.md) | django.contrib.gis (GeoDjango) | §3.2 Contrib Modules |
| [contrib-redirects-flatpages](chunks/contrib-redirects-flatpages.md) | django.contrib.redirects and django.contrib.flatpages | §3.2 Contrib Modules |

## signals (4)

| ID | Title | Source |
|----|-------|--------|
| [signals-model-save](chunks/signals-model-save.md) | pre_save / post_save (audit and cache only) | §3.3 Signals, A-001, A-008 |
| [signals-delete-m2m](chunks/signals-delete-m2m.md) | pre_delete / post_delete and m2m_changed | §3.3 Signals |
| [signals-request](chunks/signals-request.md) | request_started / request_finished | §3.3 Signals |
| [signals-auth](chunks/signals-auth.md) | user_logged_in / user_logged_out | §3.3 Signals |

## htmx-attribute (4)

| ID | Title | Source |
|----|-------|--------|
| [htmx-attr-request-verbs](chunks/htmx-attr-request-verbs.md) | Request attributes: hx-get/post/put/delete/patch | §4.1 Core Attribute Reference |
| [htmx-attr-swap-target](chunks/htmx-attr-swap-target.md) | Targeting and swapping: hx-target, hx-swap, hx-select, hx-swap-oob | §4.1 Core Attribute Reference |
| [htmx-attr-triggers-indicators](chunks/htmx-attr-triggers-indicators.md) | Triggers, indicators, values: hx-trigger, hx-indicator, hx-vals, hx-confirm | §4.1 Core Attribute Reference, A-012 |
| [htmx-attr-navigation-history](chunks/htmx-attr-navigation-history.md) | Navigation and history: hx-boost, hx-push-url, hx-history-elt, hx-preserve, hx-disable, hx-encoding, hx-ext, hx-on:* | §4.1 Core Attribute Reference, A-009 |

## htmx-pattern (9)

| ID | Title | Source |
|----|-------|--------|
| [htmx-pattern-dual-response](chunks/htmx-pattern-dual-response.md) | Dual-Response View (full page + partial from one view) | §4.2 Pattern: The Dual-Response View |
| [htmx-pattern-oob-toast](chunks/htmx-pattern-oob-toast.md) | OOB Toast + Content Update (multiple elements per response) | §4.2 Pattern: OOB Toast + Content Update |
| [htmx-pattern-active-search](chunks/htmx-pattern-active-search.md) | Active Search with Debounce | §4.2 Pattern: Active Search with Debounce |
| [htmx-pattern-inline-editing](chunks/htmx-pattern-inline-editing.md) | Inline Editing (The HTMX Way) | §4.2 Pattern: Inline Editing |
| [htmx-pattern-infinite-scroll](chunks/htmx-pattern-infinite-scroll.md) | Infinite Scroll via hx-trigger='revealed' | §4.2 Pattern: Infinite Scroll |
| [htmx-pattern-bulk-actions](chunks/htmx-pattern-bulk-actions.md) | Bulk Actions with Checkboxes | §4.2 Pattern: Bulk Actions with Checkboxes |
| [htmx-pattern-file-upload](chunks/htmx-pattern-file-upload.md) | File Upload with Progress Bar | §4.2 Pattern: File Upload with Progress |
| [htmx-middleware](chunks/htmx-middleware.md) | HTMXMiddleware for request.htmx flags | §4.3 HTMX + Django Middleware |
| [htmx-template-tags](chunks/htmx-template-tags.md) | Custom template tags for HTMX (htmx_partial, hx_attrs) | §4.4 HTMX Template Tags |

## hyperscript (6)

| ID | Title | Source |
|----|-------|--------|
| [hyperscript-install-context](chunks/hyperscript-install-context.md) | Hyperscript installation and Django template context | §5.1 Installation, §5.2 Hyperscript + Django Context |
| [hyperscript-recipe-alerts-clipboard](chunks/hyperscript-recipe-alerts-clipboard.md) | Recipes: auto-dismiss alerts and copy-to-clipboard | §5.3 Common Hyperscript Recipes |
| [hyperscript-recipe-accordion-counter](chunks/hyperscript-recipe-accordion-counter.md) | Recipes: exclusive accordion and character counter | §5.3 Common Hyperscript Recipes |
| [hyperscript-recipe-autosave](chunks/hyperscript-recipe-autosave.md) | Recipe: sticky form save indicator (autosave) | §5.3 Recipe: Sticky form save indicator |
| [hyperscript-recipe-command-palette](chunks/hyperscript-recipe-command-palette.md) | Recipe: Ctrl+K command palette | §5.3 Recipe: Command palette |
| [hyperscript-cart-pattern](chunks/hyperscript-cart-pattern.md) | Full pattern: add-to-cart with visual feedback (§5.4) | §5.4 Hyperscript + HTMX Event Integration |

## anti-pattern (15)

| ID | Title | Source |
|----|-------|--------|
| [anti-a001-signals-business-logic](chunks/anti-a001-signals-business-logic.md) | A-001: Signals for business logic | §7 A-001 |
| [anti-a002-custom-user](chunks/anti-a002-custom-user.md) | A-002: Custom User model without need | §7 A-002 |
| [anti-a003-n-plus-one](chunks/anti-a003-n-plus-one.md) | A-003: N+1 queries in templates | §7 A-003 |
| [anti-a004-logic-in-templates](chunks/anti-a004-logic-in-templates.md) | A-004: Business logic in templates | §7 A-004 |
| [anti-a005-reinvent-admin](chunks/anti-a005-reinvent-admin.md) | A-005: Reinventing the admin | §7 A-005 |
| [anti-a006-raw-sql](chunks/anti-a006-raw-sql.md) | A-006: Raw SQL without ORM fallback | §7 A-006 |
| [anti-a007-fat-views](chunks/anti-a007-fat-views.md) | A-007: Putting all logic in views | §7 A-007 |
| [anti-a008-signals-cache](chunks/anti-a008-signals-cache.md) | A-008: Signals for cache invalidation | §7 A-008 |
| [anti-a009-client-routing](chunks/anti-a009-client-routing.md) | A-009: Client-side routing for internal apps | §7 A-009 |
| [anti-a010-json-for-htmx](chunks/anti-a010-json-for-htmx.md) | A-010: JSON API for HTMX endpoints | §7 A-010 |
| [anti-a011-client-state](chunks/anti-a011-client-state.md) | A-011: State in hx-vals or data attributes | §7 A-011 |
| [anti-a012-inline-style-indicators](chunks/anti-a012-inline-style-indicators.md) | A-012: Inline styles for HTMX indicators | §7 A-012 |
| [anti-a013-no-degradation](chunks/anti-a013-no-degradation.md) | A-013: Missing graceful degradation | §7 A-013, §8 gate 5 |
| [anti-a014-over-prefetching](chunks/anti-a014-over-prefetching.md) | A-014: Over-prefetching | §7 A-014 |
| [anti-a015-genericforeignkey](chunks/anti-a015-genericforeignkey.md) | A-015: Using GenericForeignKey for routine modeling | §7 A-015 |

## workflow (2)

| ID | Title | Source |
|----|-------|--------|
| [workflow-two-phase-pipeline](chunks/workflow-two-phase-pipeline.md) | Two-phase interactivity pipeline (htmx-writer -> spa-evolver) | §6 Workflow, §2.3, §2.4 |
| [workflow-handoff-contract](chunks/workflow-handoff-contract.md) | Handoff contract and translation rules | §6.1 Handoff Contract, §2.4 Translation Rules |
