# pages/urls.py
from django.urls import path

from .views import query_search
from pages import views

urlpatterns = [
    path("", views.query_search, name="home"),
]
