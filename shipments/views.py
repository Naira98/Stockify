from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_GET
from django.http import JsonResponse
from django.views.generic import CreateView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect, render
from typing import cast
from django.contrib.admin.views.decorators import staff_member_required
from django.core.paginator import Paginator
from django.db import transaction
from accounts.models import User
from .decorators import shipment_is_pending, shipment_is_loaded
from django.urls import reverse, reverse_lazy
from inventory.models import Product
from .models import Factory, Shipment, ShipmentItem
from .forms import (
    AddShipmentItemForm,
    ShipmentForm,
    FactoryForm,
    EditShipmentItemForm,
    ShipmentFilterForm,
)
from django.db.models import Count

@login_required
def list_shipments(request):
    form = ShipmentFilterForm(request.GET or None)

    shipments = Shipment.objects.select_related("factory").annotate(
        total_items=Count("items")
    )

    selected_factory_id = request.GET.get("factory", "")
    status = request.GET.get("status", "")
    from_date = request.GET.get("from_date")
    to_date = request.GET.get("to_date")

    if selected_factory_id:
        shipments = shipments.filter(factory__id=selected_factory_id)

    if status:
        shipments = shipments.filter(status=status)

    if from_date:
        shipments = shipments.filter(created_at__date__gte=from_date)
    if to_date:
        shipments = shipments.filter(created_at__date__lte=to_date)

    # Order by newest first
    shipments = shipments.order_by("-created_at")

    paginator = Paginator(shipments, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    statuses = [
        ("pending", "Pending"),
        ("loaded", "Loaded"),
        ("received", "Received"),
    ]

    return render(
        request,
        "shipments/shipments.html",
        {
            "page_obj": page_obj,
            "shipments": page_obj.object_list,
            "form": form,
            "statuses": statuses,
            "previous_status": status,
            "selected_factory_id": selected_factory_id,
        },
    )


@login_required
@shipment_is_pending
def delete_shipment(request, pk):
    shipment = get_object_or_404(Shipment, pk=pk)
    if request.method == "POST":
        shipment.delete()
        return redirect("shipments:list_shipments")
    return redirect("shipments:shipment_details", pk=pk)


class CreateShipmentView(LoginRequiredMixin, CreateView):
    model = Shipment
    form_class = ShipmentForm
    template_name = "shipments/create_shipment.html"

    def form_valid(self, form):
        response = super().form_valid(form)
        return response

    def get_success_url(self):
        return reverse("shipments:shipment_details", kwargs={"pk": self.object.pk})  # type: ignore


class CreateFactoryView(LoginRequiredMixin, CreateView):
    model = Factory
    form_class = FactoryForm
    template_name = "shipments/create_factory.html"
    success_url = reverse_lazy("shipments:create_shipment")


class ShipmentDetailsView(LoginRequiredMixin, DetailView):
    model = Shipment
    template_name = "shipments/shipment_details.html"
    context_object_name = "shipment"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        shipment = cast(Shipment, self.get_object())

        received_user = None
        if shipment.is_received and shipment.received_by:
            try:
                received_user = User.objects.get(username=shipment.received_by)
            except User.DoesNotExist:
                received_user = None

        context["received_user"] = received_user.username if received_user else None
        return context


""" DEAL WITH SHIPMENT ITEMS """


@login_required
@shipment_is_pending
def add_item_to_shipment(request, pk):
    shipment = get_object_or_404(Shipment, pk=pk)

    if request.method == "POST":
        form = AddShipmentItemForm(request.POST)
        if form.is_valid():
            product = form.cleaned_data["product"]
            quantity = form.cleaned_data["quantity"]

            # Check if product already exists in shipment
            item, created = ShipmentItem.objects.get_or_create(
                shipment=shipment, product=product, defaults={"quantity": quantity}
            )

            if not created:
                item.quantity += quantity
                item.save()

            return redirect("shipments:shipment_details", pk=shipment.pk)
    else:
        form = AddShipmentItemForm()

    return render(
        request,
        "shipments/add_item_to_shipment.html",
        {"form": form, "shipment": shipment},
    )


@login_required
@shipment_is_pending
def edit_shipment_item(request, pk):
    item = get_object_or_404(ShipmentItem, pk=pk)
    shipment = item.shipment

    if request.method == "POST":
        form = EditShipmentItemForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
            return redirect("shipments:shipment_details", pk=shipment.pk)
    else:
        form = EditShipmentItemForm(instance=item)

    return render(
        request,
        "shipments/edit_shipment_item.html",
        {
            "form": form,
            "item": item,
            "shipment": shipment,
        },
    )


@login_required
@shipment_is_pending
def delete_shipment_item(request, pk):
    item = get_object_or_404(ShipmentItem, pk=pk)
    shipment_pk = item.shipment.pk
    item.delete()
    return redirect("shipments:shipment_details", pk=shipment_pk)


""" CHANGE SHIPMENT STATUS """


@staff_member_required
@shipment_is_pending
def mark_shipment_loaded(request, pk):
    shipment = cast(Shipment, get_object_or_404(Shipment, pk=pk))
    if shipment.items.exists():  # type: ignore
        shipment.confirm()
    return redirect("shipments:shipment_details", pk=shipment.pk)


@login_required
@shipment_is_loaded
@transaction.atomic
def mark_shipment_received(request, pk):
    shipment = get_object_or_404(Shipment, pk=pk)

    # Update the product quantities
    for item in shipment.items.select_related("product").all():  # type: ignore
        item.product.quantity += item.quantity
        item.product.save()

    shipment.mark_as_received(request.user)

    return redirect("shipments:shipment_details", pk=shipment.pk)


""" API ENDPOINT TO GET PRODUCTS BY CATEGORY """


@login_required
@require_GET
def get_products_by_category(request):
    category_id = request.GET.get("category_id")

    if category_id:
        products = Product.objects.filter(category_id=category_id)
    else:
        products = Product.objects.all()

    products = products.values("id", "name")
    return JsonResponse(list(products), safe=False)
