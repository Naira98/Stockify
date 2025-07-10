from django.urls import path
from accounts.models import User
from .views import (
    OrderListView,
    create_order,
    SupermarketCreateView,
    SupermarketListView,
    DeleteSupermarketView,
    OrderDeleteView,
    DeleteProductFromOrderView,
    AddProductToOrderView,
    EditProductInOrderView,
    ChangeOrderStatusView,
    ConfirmOrderView,
)
app_name = 'orders'


urlpatterns = [
    path("", OrderListView.as_view(), name="order_list"),
    path("create/", create_order, name="create_order"),
    path(
        "supermarket/create/",
        SupermarketCreateView.as_view(),
        name="create_supermarket",
    ),
    path("supermarket/list/", SupermarketListView.as_view(), name="supermarket_list"),
    path(
        "supermarket/<int:supermarket_id>/delete/",
        DeleteSupermarketView.as_view(),
        name="delete_supermarket",
    ),
     path('<int:pk>/', ConfirmOrderView.as_view(), name='order_details'),
      path("<int:pk>/delete/", OrderDeleteView.as_view(), name="order_delete"),
      
]