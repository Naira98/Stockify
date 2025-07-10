from django.urls import path
from .views import (
    OrderListView,
    create_order,
    edit_order,
    SupermarketCreateView,
    SupermarketListView,
    DeleteSupermarketView,
    OrderDeleteView,
    DeleteProductFromOrderView,
    ConfirmOrderView,
    OrderDetailView,
    MarkDeliveredView
)

app_name = "orders"


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
    path("<int:pk>/", OrderDetailView.as_view(), name="order_details"),
    path("<int:pk>/confirm/", ConfirmOrderView.as_view(), name="confirm_order"),
    path("<int:pk>/deliver/", MarkDeliveredView.as_view(), name="mark_delivered"),
    path("<int:pk>/edit/", edit_order, name="edit_order"),
    path("<int:pk>/delete/", OrderDeleteView.as_view(), name="order_delete"),
    path(
        "<int:order_id>/delete-product/<int:item_id>/",
        DeleteProductFromOrderView.as_view(),
        name="delete_product",
    ),
]
