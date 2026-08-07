"""MVT request lifecycle observer middleware and storage."""

import re
import threading
from collections import deque
from contextlib import contextmanager

from django.db import connection
from django.template.response import TemplateResponse
from django.test.signals import template_rendered
from django.views.generic.edit import FormView

# Keys whose POST values should be masked while keeping the dict shape.
_SENSITIVE_POST_KEYS = {
    "password",
    "csrfmiddlewaretoken",
    "csrf",
    "sessionid",
    "token",
    "secret",
    "api_key",
    "apikey",
}

_observations_lock = threading.Lock()
_observations = deque(maxlen=10)


def _clear_observations():
    """Reset the observation ring buffer (exposed for tests)."""
    with _observations_lock:
        _observations.clear()


def _sanitize_post(post):
    """Mask values for sensitive keys while keeping the dict shape."""
    sanitized = {}
    for key, value in post.lists():
        lower = key.lower()
        if any(s in lower for s in _SENSITIVE_POST_KEYS):
            sanitized[key] = ["***"] * len(value)
        else:
            sanitized[key] = list(value)
    return sanitized


def _count_errorlists(content):
    """Count Django errorlist elements in response content."""
    if not content:
        return 0
    if isinstance(content, str):
        content = content.encode("utf-8")
    return len(
        re.findall(
            rb'<[^>]*class=["\'][^"\']*errorlist[^"\']*["\']',
            content,
            re.IGNORECASE,
        )
    )


def _is_overridden(view_class, method_name):
    """Return True if ``view_class`` overrides the named FormView method."""
    return getattr(view_class, method_name) is not getattr(FormView, method_name)


@contextmanager
def _capture_templates(observation, form_errors_store):
    """Patch ``Template._render`` to emit ``template_rendered`` and capture data."""
    from django.template.base import PartialTemplate, Template
    from django.test.signals import template_rendered

    original_render = Template._render
    original_partial_render = PartialTemplate._render

    def instrumented_render(self, context):
        template_rendered.send(sender=self, template=self, context=context)
        return original_render(self, context)

    def instrumented_partial_render(self, context):
        template_rendered.send(sender=self, template=self, context=context)
        return original_partial_render(self, context)

    Template._render = instrumented_render
    PartialTemplate._render = instrumented_partial_render

    def on_template_render(sender, template, context, **kwargs):
        name = getattr(template, "name", None)
        observation["templates"].append(name)
        try:
            flat = context.flatten()
        except Exception:
            flat = {}
        observation["context_keys"].extend(list(flat.keys()))
        form = flat.get("form")
        if form is not None and hasattr(form, "errors"):
            form_errors_store.update(
                {
                    field: [str(error) for error in errors]
                    for field, errors in form.errors.items()
                }
            )

    template_rendered.connect(on_template_render)
    try:
        yield
    finally:
        template_rendered.disconnect(on_template_render)
        Template._render = original_render
        PartialTemplate._render = original_partial_render


class AgentObservationMiddleware:
    """Capture the MVT lifecycle of the current request."""

    def __init__(self, get_response):
        self.get_response = get_response

    def process_view(self, request, view_func, view_args, view_kwargs):
        """Detect class-based FormViews before dispatch."""
        view_class = getattr(view_func, "view_class", None)
        if view_class and issubclass(view_class, FormView):
            request._agent_observed_formview = view_class

    def __call__(self, request):
        observation = {
            "method": request.method,
            "path": request.path,
            "post": _sanitize_post(request.POST),
            "status_code": None,
            "content_type": None,
            "sql_count": 0,
            "sql_queries": [],
            "templates": [],
            "context_keys": [],
            "formview": None,
            "rendered_error_count": 0,
        }
        form_errors = {}
        formview_class = getattr(request, "_agent_observed_formview", None)

        original_force_debug = getattr(connection, "force_debug_cursor", False)
        connection.force_debug_cursor = True
        connection.queries_log.clear()

        try:
            with _capture_templates(observation, form_errors):
                response = self.get_response(request)
                if isinstance(response, TemplateResponse):
                    response.render()
        finally:
            observation["sql_queries"] = [
                {"sql": query.get("sql"), "time": query.get("time")}
                for query in connection.queries
            ]
            observation["sql_count"] = len(observation["sql_queries"])
            connection.force_debug_cursor = original_force_debug
            connection.queries_log.clear()

        try:
            observation["status_code"] = response.status_code
            observation["content_type"] = response.get("Content-Type", "")
            if hasattr(response, "content"):
                observation["rendered_error_count"] = _count_errorlists(
                    response.content
                )
        except Exception:
            pass

        if formview_class is not None:
            observation["formview"] = {
                "form_valid_overridden": _is_overridden(formview_class, "form_valid"),
                "form_invalid_overridden": _is_overridden(
                    formview_class, "form_invalid"
                ),
                "form_errors": form_errors,
            }

        with _observations_lock:
            _observations.append(observation)

        return response


def get_last_observation():
    """Return the most recent observation, or ``None`` if none captured."""
    with _observations_lock:
        if not _observations:
            return None
        return _observations[-1]
