from django.views.generic import TemplateView, CreateView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.urls import reverse
from inventory.models import Factory
from .models import Shipment
from .forms import ShipmentForm, FactoryForm


class ShipmentListView(TemplateView):
    template_name = "shipments/shipments.html"


class CreateShipmentView(CreateView):
    model = Shipment
    form_class = ShipmentForm
    template_name = "shipments/create_shipment.html"

    def form_valid(self, form):
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("shipment_detail", kwargs={"pk": self.get_object().pk})


class CreateFactoryView(CreateView):
    model = Factory
    form_class = FactoryForm
    template_name = "shipments/create_factory.html"
    success_url = reverse_lazy("shipments:create_shipment")


# class ShipmentDetailView(DetailView):
#     model = Shipment
#     template_name = "shipments/shipment_detail.html"
