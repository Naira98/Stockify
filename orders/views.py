from django.utils import timezone
from django import forms
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.views import View
from django.db import transaction
from .models import Order, OrderItem, Supermarket
from collections import defaultdict
from inventory.models import Product
from django.db.models import Count
from .forms import OrderForm, OrderItemForm, SupermarketForm
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import CreateView, DeleteView, ListView, DetailView
from django.forms import inlineformset_factory
from django.contrib.admin.views.decorators import staff_member_required
from .decorators import order_is_pending, order_is_confirmed
from django.db.models import F
import logging
from django.db import transaction, DatabaseError
from django.core.exceptions import ValidationError

logger = logging.getLogger(__name__)


OrderItemFormSet = inlineformset_factory(
    Order, OrderItem, form=OrderItemForm, extra=1, can_delete=True
)

class OrderListView(LoginRequiredMixin, ListView):
    model = Order
    template_name = "orders/orders_list.html"
    paginate_by = 10

    def get_queryset(self):
        queryset = Order.objects.select_related(
            "supermarket", "created_by", "confirmed_by"
        )
        status = self.request.GET.get("status", "").lower()
        search = self.request.GET.get("search", "")

        if status:
            queryset = queryset.filter(status=status)

        if search:
            queryset = queryset.filter(Q(supermarket__name__icontains=search))

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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        order = self.get_object()
        
        # Add order items
        context["order_items"] = OrderItem.objects.filter(order=order)

        # Optional: if you need categories and products too
        products = Product.objects.all()
        categories = set(product.category for product in products)
        context["products"] = products
        context["categories"] = categories

        return context


@login_required
def create_order(request):
    if request.method == "POST":
        form = OrderForm(request.POST)
        formset = OrderItemFormSet(request.POST)

        if form.is_valid() and formset.is_valid():
            with transaction.atomic():
                # Create order with Pending status
                order = form.save(commit=False)
                order.created_by = request.user
                order.status = "Pending"
                order.save()

                insufficient_stock = []
                product_quantities = defaultdict(int)

                # Collect product quantities
                for form_item in formset:
                    if form_item.cleaned_data and not form_item.cleaned_data.get("DELETE", False):
                        product = form_item.cleaned_data["product"]
                        quantity = form_item.cleaned_data["quantity"]
                        product_quantities[product] += quantity

                # Check stock availability (without deducting)
                for product, total_quantity in product_quantities.items():
                    if total_quantity > product.quantity:
                        insufficient_stock.append(
                            f"{product.name} (Available: {product.quantity}, Requested: {total_quantity})"
                        )

                if insufficient_stock:
                    messages.error(
                        request,
                        f"Insufficient stock for: {', '.join(insufficient_stock)}",
                    )
                    # Rollback the order creation if stock is insufficient
                    transaction.set_rollback(True)
                    return render(
                        request,
                        "orders/create_order.html",
                        {"form": form, "formset": formset},
                    )

                # Create order items without deducting stock
                for product, total_quantity in product_quantities.items():
                    OrderItem.objects.create(
                        order=order, 
                        product=product, 
                        quantity=total_quantity
                    )

                messages.success(request, "Order created successfully with Pending status.")
                return redirect("orders:order_list")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = OrderForm()
        formset = OrderItemFormSet()

    return render(
        request, 
        "orders/create_order.html", 
        {"form": form, "formset": formset}
    )



@login_required
@order_is_pending
def edit_order(request, pk):
    order = get_object_or_404(Order, pk=pk)
   
    OrderItemFormSet = forms.inlineformset_factory(
        Order,
        OrderItem,
        form=OrderItemForm,
        extra=1,
        can_delete=True,
        min_num=1,
        validate_min=True
    )

    if request.method == "POST":
        formset = OrderItemFormSet(request.POST, instance=order)
        if formset.is_valid():
            instances = formset.save(commit=False)
            
            # Handle deleted items - restore stock
            for obj in formset.deleted_objects:
                product = obj.product
                product.quantity += obj.quantity
                product.save()
                obj.delete()
            
            # Save remaining items
            for instance in instances:
                # If this is a new item, reduce stock
                if instance.pk is None:
                    product = instance.product
                    if instance.quantity > product.quantity:
                        messages.error(request, f"Not enough stock for {product.name}. Only {product.quantity} available.")
                        return redirect("orders:edit_order", pk=order.pk)
                    product.quantity -= instance.quantity
                    product.save()
                instance.save()
            
            messages.success(request, "Order updated successfully!")
            return redirect("orders:order_details", pk=order.pk)
    else:
        formset = OrderItemFormSet(instance=order)

    # Pre-fetch related data to optimize queries
    order_items = order.order_items.select_related('product', 'product__category').all() #type: ignore
    
    return render(
        request,
        "orders/edit_order.html",
        {
            "order": order,
            "formset": formset,
            "order_items": order_items, 
        },
    )


class SupermarketListView(LoginRequiredMixin, ListView):
    model = Supermarket
    template_name = "orders/supermarket_list.html"
    context_object_name = "supermarkets"

    def get_queryset(self):
        return Supermarket.objects.annotate(order_count=Count("order"))



@method_decorator(staff_member_required, name="dispatch")
class ConfirmOrderView(View):
    def post(self, request, pk):
        try:
            with transaction.atomic():
                # Get the order without select_related to avoid outer join issues
                order = get_object_or_404(
                    Order.objects.select_for_update(),
                    pk=pk
                )
                
                if not order.is_pending():
                    messages.error(request, "Only pending orders can be confirmed.")
                    return redirect("orders:order_details", pk=pk)

                # Get all items with locked products using prefetch_related instead
                items = list(order.order_items.select_related('product') #type: ignore
                                        .select_for_update(of=('self', 'product')))

                # Check stock availability
                insufficient_stock = []
                for item in items:
                    # No need to refresh if we properly locked the records
                    if item.product.quantity < item.quantity:
                        insufficient_stock.append(
                            f"{item.product.name} (Available: {item.product.quantity}, Required: {item.quantity})"
                        )

                if insufficient_stock:
                    messages.error(
                        request, 
                        f"Insufficient stock for: {', '.join(insufficient_stock)}"
                    )
                    return redirect("orders:order_details", pk=pk)

                # Update stock quantities
                for item in items:
                    updated = Product.objects.filter(
                        pk=item.product.pk,
                        quantity__gte=item.quantity
                    ).update(
                        quantity=F("quantity") - item.quantity
                    )
                    if not updated:
                        raise ValidationError(
                            f"Concurrent modification detected for product {item.product.name}"
                        )

                # Update order status
                order.status = "Confirmed"
                order.confirmed_by = request.user
                order.save(update_fields=['status', 'confirmed_by'])

        except DatabaseError as e:
            logger.error(f"Database error confirming order {pk}: {str(e)}", exc_info=True)
            messages.error(request, "A database error occurred. Please try again.")
        except ValidationError as e:
            logger.error(f"Validation error confirming order {pk}: {str(e)}")
            messages.error(request, str(e))
        except Exception as e:
            logger.error(f"Unexpected error confirming order {pk}: {str(e)}", exc_info=True)
            messages.error(request, "An unexpected error occurred while confirming the order.")
        else:
            messages.success(request, "Order confirmed successfully.")
        
        return redirect("orders:order_details", pk=pk)



@method_decorator(login_required, name="dispatch")
@method_decorator(order_is_confirmed, name="dispatch")
class MarkDeliveredView(View):
    def post(self, request, pk):
        # No need to get order again - decorator already did it
        order = request.order
        
        with transaction.atomic():
            order.status = "Delivered"
            order.delivery_date = timezone.now()
            order.save()

        messages.success(request, "Order marked as delivered.")
        return redirect("orders:order_details", pk=pk)

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



@method_decorator(staff_member_required, name="dispatch")
class DeleteSupermarketView(View):
    def post(self, request, supermarket_id):
        supermarket = get_object_or_404(Supermarket, id=supermarket_id)

        with transaction.atomic():
            orders = Order.objects.filter(supermarket=supermarket)

            for order in orders:
                if order.status == "Pending":
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
