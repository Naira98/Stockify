
from django.urls import path
from .views import InventoryListView

app_name = 'inventory'

urlpatterns = [
    path('', InventoryListView.as_view(), name='inventory'),
]