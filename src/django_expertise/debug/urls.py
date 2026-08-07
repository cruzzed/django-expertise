"""URLconf for the agent debug endpoints."""

from django.urls import path

from django_expertise.debug.views import agent_last_request

urlpatterns = [
    path("last-request/", agent_last_request, name="agent_last_request"),
]
