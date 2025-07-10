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
    
@method_decorator(login_required, name="dispatch")
class ConfirmOrderView(View):
    def post(self, request, pk):
        order = get_object_or_404(Order, pk=pk)

        if not request.user.is_manager():
            messages.error(request, "Only managers can confirm orders.")
            return redirect("orders:order_detail", pk=pk)

        if order.status != "pending":
            messages.error(request, "Only pending orders can be confirmed.")
            return redirect("orders:order_detail", pk=pk)

        order_items = OrderItem.objects.filter(order=order).select_related("product")
        insufficient_stock = []

        for item in order_items:
            if item.product.current_quantity < item.quantity:  # type: ignore
                insufficient_stock.append(
                    f"{item.product.name} (Available: {item.product.current_quantity}, Required: {item.quantity})"  # type: ignore
                )

        if insufficient_stock:
            messages.error(
                request, f"Insufficient stock for: {', '.join(insufficient_stock)}"
            )
            return redirect("orders:order_detail", pk=pk)

        with transaction.atomic():
            for item in order_items:
                item.product.current_quantity -= item.quantity  # type: ignore
                item.product.save()

            order.status = "confirmed"
            order.confirmed_by = request.user
            order.save()

        messages.success(request, "Order confirmed successfully.")
        return redirect("orders:order_detail", pk=pk)


class OrderDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Order
    template_name = "orders/order_confirm_delete.html"
    success_url = reverse_lazy("orders:order_list")

    def test_func(self):

        order = self.get_object()
        return order.status not in ["Confirmed", "Delivered"]  # type: ignore

    def delete(self, request, *args, **kwargs):

        order = self.get_object()

        for item in order.items.all():  # type: ignore
            product = item.product
            product.quantity += item.quantity
            product.save()

        messages.success(
            request, "Order has been successfully deleted and stock restored."
        )
        return super().delete(request, *args, **kwargs)

    def handle_no_permission(self):  # type: ignore
        """
        If test_func fails (i.e., the order is confirmed or delivered)
        """
        order = self.get_object()
        messages.error(
            self.request,
            "This order cannot be deleted because it is already confirmed or delivered.",
        )
        return redirect("orders:order_details", order_id=order.pk)


def manager_required(view_func):
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_manager():
            messages.error(request, "Only managers can perform this action.")
            return redirect("orders:supermarket_list")
        return view_func(request, *args, **kwargs)

    return _wrapped_view

@method_decorator([login_required, manager_required], name="dispatch")
class DeleteSupermarketView(View):
    def post(self, request, supermarket_id):
        supermarket = get_object_or_404(Supermarket, id=supermarket_id)

        with transaction.atomic():
            orders = Order.objects.filter(supermarket=supermarket)

            for order in orders:
                if order.status in ["Pending", "Loaded"]:
                    for item in order.items.all():  # type: ignore
                        item.product.quantity += item.quantity
                        item.product.save()

            orders.delete()
            supermarket.delete()

            messages.success(
                request, "Supermarket and related orders have been deleted."
            )

        return redirect("orders:supermarket_list")
    

@method_decorator(login_required, name="dispatch")
class DeleteProductFromOrderView(View):
    def post(self, request, order_id, item_id):
        order = get_object_or_404(Order, id=order_id)
        item = get_object_or_404(OrderItem, id=item_id, order_id=order_id)

        # Check if order is not editable
        if order.status in ["Confirmed", "Delivered"]:
            messages.error(
                request,
                "You cannot delete the product as it has been already confirmed or delivered.",
            )
            return redirect("orders:order_details", order_id=order.pk)

        product = item.product
        item.delete()

        messages.success(
            request,
            f"{product.name} was removed from the order, and stock was restored.",
        )
        return redirect("orders:order_details", order_id=order.pk)

@method_decorator([login_required, manager_required], name="dispatch")
class ChangeOrderStatusView(View):
    def post(self, request, order_id):
        order = get_object_or_404(Order, id=order_id)
        status_flow = ["Pending", "Confirmed", "Delivered"]

        if order.status == "Delivered":
            messages.error(request, "Delivered orders cannot be modified.")
        else:
            try:
                current_index = status_flow.index(order.status)
                new_status = status_flow[current_index + 1]
                order.status = new_status
                order.save()
                messages.success(request, f"Order status updated to {new_status}.")
            except (ValueError, IndexError):
                messages.error(request, "Invalid status transition.")

        return redirect("orders:order_details", order_id=order.pk)
