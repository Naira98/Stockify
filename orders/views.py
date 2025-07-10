from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.views import View
# from .decorators import manager_required
from django.db import transaction
from .models import Order, OrderItem, Supermarket
from collections import defaultdict
from inventory.models import Product
from django.db.models import Count
from .forms import OrderForm, OrderItemForm
from .forms import SupermarketForm
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import CreateView, DeleteView, ListView, DetailView
from django.forms import inlineformset_factory
from django.contrib.admin.views.decorators import staff_member_required

# Create your views here.
class OrderListView(LoginRequiredMixin, ListView):
    model = Order
    context_object_name = "page_obj"
    template_name = "orders/orders_list.html"
    paginate_by = 20

    def get_queryset(self):
        queryset = Order.objects.select_related(
            "supermarket", "created_by", "confirmed_by"
        )
        status = self.request.GET.get("status", "")
        search = self.request.GET.get("search", "")

        if status:
            queryset = queryset.filter(status=status)

        if search:
            queryset = queryset.filter(
                Q(supermarket__name__icontains=search) | Q(notes__icontains=search)
            )

        return queryset
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["status_filter"] = self.request.GET.get("status", "")
        context["search_query"] = self.request.GET.get("search", "")
        context["status_choices"] = Order.STATUS_CHOICES
        return context
    
@method_decorator(staff_member_required, name="dispatch")
class SupermarketCreateView(LoginRequiredMixin, CreateView):
    model = Supermarket
    form_class = SupermarketForm
    template_name = "orders/create_supermarket.html"
    success_url = reverse_lazy("orders:create_order")

    def form_valid(self, form):
        response = super().form_valid(form)

        if "_addanother" in self.request.POST:
            return redirect("orders:create_supermarket")

        return response
    
