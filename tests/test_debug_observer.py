"""Tests for the MVT request lifecycle observer."""

import unittest

from django import forms
from django.db import connection
from django.http import HttpResponse
from django.template import engines
from django.test import Client, RequestFactory
from django.urls import include, path, resolve
from django.views.generic.edit import FormView

from django_expertise.debug.observer import (
    AgentObservationMiddleware,
    _clear_observations,
    get_last_observation,
)


def normal_view(request):
    return HttpResponse("ok")


def sql_view(request):
    with connection.cursor() as cursor:
        cursor.execute("SELECT 1")
    return HttpResponse("ok")


def template_view(request):
    template = engines["django"].from_string(
        "<html><body>{% if greeting %}{{ greeting }}{% endif %}</body></html>"
    )
    return HttpResponse(template.render({"greeting": "hi"}))


class SampleForm(forms.Form):
    name = forms.CharField()
    email = forms.EmailField()


class UnimplementedFormView(FormView):
    template_name = "test_form.html"
    form_class = SampleForm
    success_url = "/done/"


class OverriddenFormView(FormView):
    template_name = "test_form.html"
    form_class = SampleForm
    success_url = "/done/"

    def form_valid(self, form):
        return HttpResponse("custom valid")

    def form_invalid(self, form):
        return HttpResponse("custom invalid")


urlpatterns = [
    path("normal/", normal_view, name="normal"),
    path("sql/", sql_view, name="sql"),
    path("template/", template_view, name="template"),
    path("form/", UnimplementedFormView.as_view(), name="form"),
    path("form-overridden/", OverriddenFormView.as_view(), name="form_overridden"),
    path("__agent__/", include("django_expertise.debug.urls")),
]


class ObserverMiddlewareTests(unittest.TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        _clear_observations()

    def _make_request(self, request, view=None):
        if view is None:
            view = normal_view
        middleware = AgentObservationMiddleware(view)
        resolved = resolve(request.path)
        middleware.process_view(request, resolved.func, resolved.args, resolved.kwargs)
        return middleware(request)

    def test_normal_request_records_method_path_status(self):
        request = self.factory.get("/normal/")
        response = self._make_request(request)
        self.assertEqual(response.status_code, 200)
        obs = get_last_observation()
        self.assertEqual(obs["method"], "GET")
        self.assertEqual(obs["path"], "/normal/")
        self.assertEqual(obs["status_code"], 200)

    def test_sql_queries_are_counted(self):
        request = self.factory.get("/sql/")
        response = self._make_request(request, view=sql_view)
        self.assertEqual(response.status_code, 200)
        obs = get_last_observation()
        self.assertEqual(obs["sql_count"], 1)
        self.assertIn("SELECT 1", obs["sql_queries"][0]["sql"])

    def test_template_names_and_context_keys(self):
        request = self.factory.get("/template/")
        response = self._make_request(request, view=template_view)
        self.assertEqual(response.status_code, 200)
        obs = get_last_observation()
        self.assertEqual(obs["templates"], [None])
        self.assertIn("greeting", obs["context_keys"])

    def test_post_data_is_redacted(self):
        request = self.factory.post(
            "/normal/",
            data={
                "name": "Franki",
                "password": "supersecret",
                "csrfmiddlewaretoken": "abc123",
            },
        )
        self._make_request(request)
        obs = get_last_observation()
        self.assertEqual(obs["post"]["name"], ["Franki"])
        self.assertEqual(obs["post"]["password"], ["***"])
        self.assertEqual(obs["post"]["csrfmiddlewaretoken"], ["***"])

    def test_formview_unimplemented_records_state_and_errors(self):
        request = self.factory.post(
            "/form/",
            data={"name": "Franki", "email": "not-an-email"},
        )
        response = self._make_request(request, view=UnimplementedFormView.as_view())
        self.assertEqual(response.status_code, 200)
        obs = get_last_observation()
        self.assertIsNotNone(obs["formview"])
        self.assertFalse(obs["formview"]["form_valid_overridden"])
        self.assertFalse(obs["formview"]["form_invalid_overridden"])
        self.assertIn("email", obs["formview"]["form_errors"])
        self.assertGreater(obs["rendered_error_count"], 0)

    def test_formview_overridden_detected(self):
        request = self.factory.post(
            "/form-overridden/",
            data={"name": "Franki", "email": "not-an-email"},
        )
        response = self._make_request(request, view=OverriddenFormView.as_view())
        self.assertEqual(response.content, b"custom invalid")
        obs = get_last_observation()
        self.assertTrue(obs["formview"]["form_valid_overridden"])
        self.assertTrue(obs["formview"]["form_invalid_overridden"])


class AgentEndpointTests(unittest.TestCase):
    def setUp(self):
        _clear_observations()
        self.client = Client()

    def test_last_request_endpoint_returns_json(self):
        self.client.get("/normal/")
        response = self.client.get("/__agent__/last-request/")
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["observation"]["method"], "GET")
        self.assertEqual(payload["observation"]["path"], "/normal/")

    def test_endpoint_returns_null_when_no_observation(self):
        response = self.client.get("/__agent__/last-request/")
        self.assertEqual(response.status_code, 200)
        self.assertIsNone(response.json()["observation"])


if __name__ == "__main__":
    unittest.main()
