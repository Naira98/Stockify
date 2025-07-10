
from django.urls import path

from inventory import views
from inventory.views import Addcategoryview, DeleteCategoryConfirmView, DeleteCategoryView, InventoryListView, AddProductView, ProductDeleteView, ProductUpdateView, Productdetailview

app_name = 'inventory'

urlpatterns = [
    path('', InventoryListView.as_view(), name='inventory'),
    path('add/', AddProductView.as_view(), name='addproduct'),
    path('<int:pk>/', Productdetailview.as_view(), name='details'),
    path('addcategory/',Addcategoryview.as_view(), name='addcategory'),
    path('category/delete/', DeleteCategoryView.as_view(), name='deletecategory'),
    path('category/delete/<int:pk>/', DeleteCategoryConfirmView.as_view(), name='deletecategoryconfirm'),
    path('delete/<int:pk>/',ProductDeleteView.as_view(), name='deleteproduct'),
    path('edit/<int:pk>/', ProductUpdateView.as_view(), name='editproduct'),
]