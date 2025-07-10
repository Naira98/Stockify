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
    
]