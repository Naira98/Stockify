from django.urls import path
from accounts.models import User
from django import forms
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
    path(
        "<int:order_id>/delete-product/<int:item_id>/",
        DeleteProductFromOrderView.as_view(),
        name="delete_product",
    ),
    path(
        "<int:order_id>/add-product/",
        AddProductToOrderView.as_view(),
        name="add_product_to_order",
    ),
    path(
        "<int:order_id>/edit-product/<int:product_id>/",
        EditProductInOrderView.as_view(),
        name="edit_product_in_order",
    ),
    path(
        "<int:order_id>/change-status/",
        ChangeOrderStatusView.as_view(),
        name="change_order_status",
    ),
]

class AdminUserEditForm(forms.ModelForm):
    ROLE_CHOICES = (
        ("admin", "Admin"),
        ("employee", "Employee"),
    )

    role = forms.ChoiceField(
        choices=ROLE_CHOICES,
        required=True,
        label="User Role",
        widget=forms.RadioSelect(attrs={"class": "flex space-x-4"}),
        initial="employee",
    )

    class Meta:
        model = User
        fields = ["username", "email", "first_name", "last_name", "role"]

        def save(self, commit=True):
            user = super().save(commit=False)
            role = self.cleaned_data.get("role")

            if role == "admin":
                user.is_superuser = True
                user.is_staff = True
                user.is_user = False
            else:
                user.is_superuser = False
                user.is_staff = False
                user.is_user = True

            if commit:
                user.save()
            return user