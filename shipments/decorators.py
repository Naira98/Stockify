from django.shortcuts import get_object_or_404, redirect
from functools import wraps
from .models import Shipment

# Generic decorator
def shipment_status_required(check_func, redirect_view_name="shipments:shipment_details"):
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
shipment_is_pending = shipment_status_required(lambda s: s.is_pending())
shipment_is_loaded = shipment_status_required(lambda s: s.is_loaded())
shipment_is_received = shipment_status_required(lambda s: s.is_received())
