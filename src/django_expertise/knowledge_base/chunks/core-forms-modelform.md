# django.forms Form and ModelForm

- **ID:** `core-forms-modelform`
- **Category:** django-core
- **Source:** §3.1 Core Framework
- **Tags:** `forms`, `modelform`, `validation`

## Canonical pattern (Django / HTMX / Hyperscript way)
django.forms.Form declares fields with validation (clean_<field>(), clean()); ModelForm derives the form from a model via Meta.model/Meta.fields and form.save() persists. Forms own input validation - never validate in templates or views by hand.

## Typical MVC default (what AI typically generates)
Typical MVC frameworks validate inline in the controller plus hand-written form markup, or use a client-side form library on the frontend. AI often validates in the view with ad-hoc dict checks instead of a form class.

## Why Django differs
Django forms are a dedicated, reusable validation/rendering layer: they render HTML, normalize input, run validators, and ModelForm maps directly to the ORM. Inline controller validation duplicates rules and scatters them across views.

## Example
from django import forms
from .models import Task

class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['title', 'due_date', 'status']

    def clean_title(self):
        t = self.cleaned_data['title']
        if len(t) < 3:
            raise forms.ValidationError("Too short")
        return t
