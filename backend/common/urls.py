from django.urls import path

from . import views


# To help delegate rendering to frontend
app_name = "common"
urlpatterns = [
    path("", views.IndexView.as_view(), name="index"),
]
