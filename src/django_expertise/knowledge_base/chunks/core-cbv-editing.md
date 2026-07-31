# Editing CBVs: FormView, CreateView, UpdateView, DeleteView

- **ID:** `core-cbv-editing`
- **Category:** django-core
- **Source:** §3.1 Core Framework, §2.2 CBV Decision Matrix
- **Tags:** `cbv`, `crud`, `forms`

## Canonical pattern (Django / HTMX / Hyperscript way)
Use CreateView/UpdateView/DeleteView for model-form CRUD and FormView for non-model forms. Set model, form_class (or fields), template_name and success_url (or get_success_url()). Avoid them for multi-step wizards, inline HTMX edits (use partials), or soft deletes.

## Laravel / MVC default (what AI typically generates)
Laravel: a controller with store/update/destroy methods doing request->validate + Model::create($validated) by hand, returning redirects. AI writes manual create/update logic instead of declaring a generic view.

## Why Django differs
Django's generic editing CBVs encode the entire GET-form/POST-validate/save/redirect cycle declaratively. Overriding hooks (form_valid, get_success_url) is the extension point; reimplementing the cycle in every view is boilerplate the framework already solved.

## Example
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy

class TaskCreateView(LoginRequiredMixin, CreateView):
    model = Task
    form_class = TaskForm
    template_name = 'tasks/form.html'
    success_url = reverse_lazy('task-list')

class TaskDeleteView(DeleteView):
    model = Task
    success_url = reverse_lazy('task-list')
