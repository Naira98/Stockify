from django.db import models
from django.core.exceptions import ValidationError
from inventory.models import Product
from django.db import transaction
from accounts.models import User
from stockify.models import TimestampModel
 
 
class Supermarket(TimestampModel):
    name = models.CharField(max_length=255, unique=True)
    location = models.TextField()
 
    def __str__(self):
        return self.name
 
 
class Order(TimestampModel):
    STATUS_CHOICES = [
        ("Pending", "Pending"),
        ("Confirmed", "Confirmed"),
        ("Delivered", "Delivered"),
    ]
 
    supermarket = models.ForeignKey(Supermarket, on_delete=models.CASCADE)
    delivery_date = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="pending")
    created_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="created_orders"
    )
    confirmed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="confirmed_orders",
    )
 
    def __str__(self):
        return f"Order for {self.supermarket.name}"
 
    def total_items(self):
        return sum(item.quantity for item in self.order_items.all()) # type: ignore
 
    def add_product(self, product, quantity):
        if quantity > product.quantity:
            return f"Limited stock: only {product.quantity} units left."
 
        order = OrderItem.objects.filter(order=self, product=product).first()
 
        if not order:
            order = OrderItem(order=self, product=product, quantity=0)
            order.save()
            created = True
        else:
            created = False
 
    def update_product(self, product, new_quantity):
        """
        Updates the quantity of a product in the order.
        """
        try:
            order = OrderItem.objects.get(order=self, product=product)
        except OrderItem.DoesNotExist:
            return f"{product.name} is not included in this order."
 
        difference = new_quantity - order.quantity
 
        if difference > product.quantity:
            return f"Insufficient stock for {product.name}. Only {product.quantity} units available."
 
        order.quantity = new_quantity
        product.quantity -= difference
 
        product.save()
        order.save()
 
        return None
 
    def remove_product_alternative(self, product):
        """
            Removes a product from the order and restores its stock (alternative approach).
            - Uses transaction for atomicity
        - Checks product validity before processing
        - More verbose error handling
        """
        with transaction.atomic():  # Ensure all operations succeed or fail together
            # Check if product exists in the order (alternative query style)
            if not OrderItem.objects.filter(order=self, product=product).exists():
                raise ValidationError(f"Product '{product.name}' is not in this order.")
 
        # Get the order item and product data in one query
        order_item = OrderItem.objects.select_for_update().get(
            order=self, product=product
        )
 
        # Restore stock (with overflow check)
        new_quantity = product.quantity + order_item.quantity
        if new_quantity < 0:  # Prevent negative stock
            raise ValidationError("Invalid stock operation: Negative quantity")
 
        # Perform updates
        product.quantity = new_quantity
        product.save()
        order_item.delete()
 
        return f"Removed {order_item.quantity} of {product.name} from order"
 
 
class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='order_items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
 
    def __str__(self):
        return f"{self.product.name} - {self.quantity}"
 
    def delete(self, *args, **kwargs):
        product = self.product
        quantity_to_restore = self.quantity
 
        # Restore stock
        product.quantity = product.quantity + quantity_to_restore
        product.save(update_fields=["quantity"])
 
        # Proceed with deletion
        return super(OrderItem, self).delete(*args, **kwargs)
