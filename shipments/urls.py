from django.urls import path
from shipments import views


urlpatterns = [
    path("", views.ShipmentsPage.as_view(), name="shipments"),
]
