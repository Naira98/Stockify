from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_GET
from django.http import JsonResponse
from django.views.generic import TemplateView, CreateView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect, render
from .decorators import shipment_is_not_loaded
from django.urls import reverse, reverse_lazy
from inventory.models import Factory, Product
from .models import Shipment, ShipmentItem
from .forms import AddShipmentItemForm, ShipmentForm, FactoryForm, EditShipmentItemForm


class ShipmentListView(TemplateView, LoginRequiredMixin):
    template_name = "shipments/shipments.html"


class CreateShipmentView(CreateView, LoginRequiredMixin):
    model = Shipment
    form_class = ShipmentForm
    template_name = "shipments/create_shipment.html"

    def form_valid(self, form):
        response = super().form_valid(form)
        return response

    def get_success_url(self):
        return reverse("shipments:shipment_details", kwargs={"pk": self.object.pk})  # type: ignore


class CreateFactoryView(CreateView, LoginRequiredMixin):
    model = Factory
    form_class = FactoryForm
    template_name = "shipments/create_factory.html"
    success_url = reverse_lazy("shipments:create_shipment")


class ShipmentDetailsView(DetailView, LoginRequiredMixin):
    model = Shipment
    template_name = "shipments/shipment_details.html"
    context_object_name = "shipment"


@login_required
@shipment_is_not_loaded
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
@shipment_is_not_loaded
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
@shipment_is_not_loaded
def delete_shipment_item(request, pk):
    item = get_object_or_404(ShipmentItem, pk=pk)
    shipment_pk = item.shipment.pk
    item.delete()
    return redirect("shipments:shipment_details", pk=shipment_pk)


# API endpoint to get products by category
@login_required
@require_GET
def get_products_by_category(request):
    category_id = request.GET.get("category_id")
    if not category_id:
        return JsonResponse({"error": "Missing category_id"}, status=400)

    products = Product.objects.filter(category_id=category_id).values("id", "name")
    return JsonResponse(list(products), safe=False)
