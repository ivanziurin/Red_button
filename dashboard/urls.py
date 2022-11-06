from django.urls import path

from .views import my_chart

urlpatterns = [
    path("dashboard/data/", my_chart, name="my-chart"),
]