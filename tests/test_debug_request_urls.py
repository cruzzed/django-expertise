from django.http import HttpResponse
from django.urls import path


def hello(request):
    return HttpResponse("Hello from django-expertise debug test")


urlpatterns = [
    path("", hello, name="hello"),
]
