from django.urls import path
from shipments import views

app_name = "shipments"

urlpatterns = [
    path("", views.ShipmentListView.as_view(), name="list_shipments"),
    path("create/", views.CreateShipmentView.as_view(), name="create_shipment"),
    path("factories/create/", views.CreateFactoryView.as_view(), name="create_factory"),
]

# # shipment_list
# create_shipment
# create_factory
# shipment_detail
# add_product_to_shipment
# edit_shipment_item_quantity
# delete_product_from_shipment
# delete_shipment
# mark_shipment_as_loaded
# mark_shipment_as_received

