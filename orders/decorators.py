from functools import wraps
from django.shortcuts import get_object_or_404, redirect
from .models import Order

from django.db import transaction

def order_status_required(check_func, redirect_view_name="orders:order_details"):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            # Start transaction here to wrap the select_for_update
            with transaction.atomic():
                order = get_object_or_404(
                    Order.objects.select_for_update(),
                    pk=kwargs.get("pk")
                )
                if not check_func(order):
                    return redirect(redirect_view_name, pk=order.pk)
                request.order = order
                return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator

# Create decorator instances
order_is_pending = order_status_required(lambda o: o.status == "Pending")
order_is_confirmed = order_status_required(lambda o: o.status == "Confirmed")
order_is_delivered = order_status_required(lambda o: o.status == "Delivered")
