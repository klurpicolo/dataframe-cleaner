from django.urls import path

from . import views


# To help delegate rendering to frontend
app_name = "common"
urlpatterns = [
    path("", views.IndexView.as_view(), name="index"),
    path("about", views.IndexView.as_view(), name="index"),
    path("homeklur", views.IndexView.as_view(), name="index"),
    path("dataframev1", views.IndexView.as_view(), name="index"),
]
