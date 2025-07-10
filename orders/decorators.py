from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse


def manager_required(view_func):
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_manager():
            messages.error(request, "Only managers can perform this action.")
            return redirect(
                request.META.get("HTTP_REFERER", reverse("orders:order_list"))
            )
        return view_func(request, *args, **kwargs)

    return _wrapped_view
