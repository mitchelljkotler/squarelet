# Django
from django.urls import path

# Local
from .views import get, ping

urlpatterns = [
    path("get", get, name="get_csrf_token"),
    path("ping", ping, name="ping_csrf_token"),
]