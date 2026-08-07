"""JSON endpoint for the last captured request observation."""

from django.http import JsonResponse

from django_expertise.debug.observer import get_last_observation


def agent_last_request(request):
    """Return the last captured MVT observation as JSON."""
    return JsonResponse({"observation": get_last_observation()})
