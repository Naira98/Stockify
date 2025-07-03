from django.urls import path
from shipments import views

app_name = "shipments"

urlpatterns = [
    path("", views.ShipmentListView.as_view(), name="shipment_list"),
    path("<int:pk>/delete/", views.delete_shipment, name="delete_shipment"),
    path("<int:pk>/", views.ShipmentDetailsView.as_view(), name="shipment_details"),
    path("create/", views.CreateShipmentView.as_view(), name="create_shipment"),
    path("factories/create/", views.CreateFactoryView.as_view(), name="create_factory"),
    path(
        "<int:pk>/add-item/",
        views.add_item_to_shipment,
        name="add_shipment_item",
    ),
    path("items/<int:pk>/edit/", views.edit_shipment_item, name="edit_shipment_item"),
    path(
        "item/<int:pk>/delete/", views.delete_shipment_item, name="delete_shipment_item"
    ),
    path("<int:pk>/mark-loaded/", views.mark_shipment_loaded, name="mark_loaded"),
    path("<int:pk>/mark-received/", views.mark_shipment_received, name="mark_received"),
    path(
        "api/products/", views.get_products_by_category, name="get_products_by_category"
    ),
]

# # shipment_list
# create_shipment
# create_factory
# shipment_detail
# add_item_to_shipment
# edit_shipment_item_quantity
# delete_product_from_shipment
# delete_shipment
# mark_shipment_as_loaded
# mark_shipment_as_received
