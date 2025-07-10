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
]