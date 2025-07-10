from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.views import View
# from .decorators import manager_required
from django.db import transaction
from .models import Order, OrderItem, Supermarket
from collections import defaultdict
from inventory.models import Product , Category
from django.db.models import Count
from .forms import OrderForm, OrderItemForm
from .forms import OrderForm, OrderItemFormSet, SupermarketForm
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
    
class OrderDetailView(LoginRequiredMixin, DetailView):
    model = Order
    template_name = "orders/order_details.html"
    context_object_name = "order"
    pk_url_kwarg = "order_id"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        products = Product.objects.all()
        categories = set(product.category for product in products)
        context["products"] = products
        context["categories"] = categories
        return context

OrderItemFormSet = inlineformset_factory(
    Order, OrderItem, form=OrderItemForm, extra=1, can_delete=True
) 

@login_required
def create_order(request):
    if request.method == "POST":
        form = OrderForm(request.POST)
        formset = OrderItemFormSet(request.POST)

        if form.is_valid() and formset.is_valid():
            with transaction.atomic():
                order = form.save(commit=False)
                order.created_by = request.user
                order.status = "confirmed"
                order.save()

                insufficient_stock = []
                product_quantities = defaultdict(int)

                # Collect product quantities
                for form_item in formset:
                    if form_item.cleaned_data and not form_item.cleaned_data.get(
                        "DELETE", False
                    ):
                        product = form_item.cleaned_data["product"]
                        quantity = form_item.cleaned_data["quantity"]
                        product_quantities[product] += quantity

                # Check stock
                for product, total_quantity in product_quantities.items():
                    if total_quantity > product.quantity:
                        insufficient_stock.append(
                            f"{product.name} (Available: {product.quantity})"
                        )

                if insufficient_stock:
                    messages.error(
                        request,
                        f"Not enough stock for: {', '.join(insufficient_stock)}.",
                    )
                    return render(
                        request,
                        "orders/create_order.html",
                        {"form": form, "formset": formset},
                    )

                # Deduct stock & create OrderItems
                for product, total_quantity in product_quantities.items():
                    product.quantity -= total_quantity
                    product.save()

                    OrderItem.objects.create(
                        order=order, product=product, quantity=total_quantity
                    )

                messages.success(request, "Order created successfully.")
                return redirect("orders:order_list")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = OrderForm()
        formset = OrderItemFormSet()

    return render(
        request, "orders/create_order.html", {"form": form, "formset": formset}
    )

class SupermarketListView(LoginRequiredMixin, ListView):
    model = Supermarket
    template_name = "orders/supermarket_list.html"
    context_object_name = "supermarkets"

    def get_queryset(self):
        return Supermarket.objects.annotate(order_count=Count("order"))