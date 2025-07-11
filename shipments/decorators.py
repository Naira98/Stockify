from django.shortcuts import get_object_or_404, redirect
from functools import wraps
from django.http import Http404
from .models import Shipment, ShipmentItem


# Generic decorator
def shipment_status_required(
    check_func, redirect_view_name="shipments:shipment_details"
):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            shipment = get_object_or_404(Shipment, pk=kwargs.get("pk"))
            if not check_func(shipment):
                return redirect(redirect_view_name, pk=shipment.pk)
            request.shipment = shipment
            return view_func(request, *args, **kwargs)

        return _wrapped_view

    return decorator


# Specific decorators
shipment_is_loaded = shipment_status_required(lambda s: s.is_loaded())



def shipment_is_pending(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        pk = kwargs.get("pk")

        # Try: pk is Shipment pk
        shipment = Shipment.objects.filter(pk=pk, status="pending").first()

        # Try: pk is ShipmentItem pk
        if not shipment:
            try:
                item = ShipmentItem.objects.select_related("shipment").get(pk=pk)
                shipment = item.shipment
            except ShipmentItem.DoesNotExist:
                pass

        if not shipment or not shipment.is_pending:
            raise Http404("No pending shipment found.")

        return view_func(request, *args, **kwargs)

    return _wrapped_view
