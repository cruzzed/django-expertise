# Display CBVs: ListView, DetailView, TemplateView, RedirectView

- **ID:** `core-cbv-display`
- **Category:** django-core
- **Source:** §3.1 Core Framework, §2.2 CBV Decision Matrix
- **Tags:** `cbv`, `listview`, `detailview`, `pagination`

## Canonical pattern (Django / HTMX / Hyperscript way)
ListView gives paginated object listing (paginate_by, context_object_name, get_queryset); DetailView renders one object; TemplateView renders a static page with extra context; RedirectView handles simple redirects. Use django-filter for custom filtering UIs instead of bloating ListView.

## Laravel / MVC default (what AI typically generates)
Laravel: Product::paginate(20) in a controller method then view('products.index', compact(...)) with all query logic inline. Rails: @products = Product.page(params[:page]) in the controller.

## Why Django differs
Django declaratively binds model, queryset, pagination and template on the class. get_queryset() is the documented hook for query optimization (prefetch_related) - keeping controllers thin and query logic in one overridable place.

## Example
from django.views.generic import ListView, DetailView

class ProductListView(LoginRequiredMixin, ListView):
    model = Product
    template_name = 'products/list.html'
    context_object_name = 'products'
    paginate_by = 20

    def get_queryset(self):
        return Product.objects.prefetch_related('category', 'tags')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['categories'] = Category.objects.all()
        return ctx
