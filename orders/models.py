from django.db import models
from accounts.models import User
from inventory.models import Product, Category
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.db import transaction
from stockify.models import TimestampModel
from django.db import transaction


# Create your models here.



class Supermarket(models.Model):
    """Supermarket model for customers"""
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=100)


    def __str__(self):
        return self.name


class Order(models.Model):
    """Order model for outgoing products to supermarkets"""
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Confirmed', 'Confirmed'),
         ('Delivered', 'Delivered'),
    ]
    supermarket = models.ForeignKey(Supermarket, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    delivery_date = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_orders')
    confirmed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='confirmed_orders')
    products = models.ManyToManyField(Product, through='OrderItem')

    def __str__(self):
        return f"Order #{self.id} to {self.supermarket.name}"
    

    def confirm_order(self, confirmed_by):
        """Confirm order and update product quantities"""
        if self.status == 'pending':
            self.status = 'confirmed'
            self.confirmed_by = confirmed_by
            self.confirmed_at = timezone.now()
            self.save()
            
            # Update product quantities
            for item in self.orderitem_set.all():
                if item.product.current_quantity >= item.quantity:
                    item.product.current_quantity -= item.quantity
                    item.product.save()

    def add_product(self, product, quantity):         
        if quantity <= 0:
            return "Quantity must be greater than zero."
    
    # Order status validation
        if self.status != 'pending':
            return "Products can only be added to pending orders."   
        
        if quantity > product.current_quantity:
            return f"Insufficient stock. Available: {product.current_quantity}"
        
        with transaction.atomic():
        # Get or create order item
            order_item, created = OrderItem.objects.get_or_create(
            order=self,
            product=product,
            defaults={'quantity': quantity}
        )

        if self.status == 'confirmed':
            if product.current_quantity < quantity:
                raise ValidationError(
                    f"Insufficient stock for {product.name}. "
                    f"Available: {product.current_quantity}, Requested: {quantity}"
                )
        order_item, created = OrderItem.objects.get_or_create(
            order=self,
            product=product,
            defaults={'quantity': quantity}
        )
        if not created:
               order_item.quantity += quantity
               order_item.save()

               product.current_quantity -= quantity
               product.save()
    
        return None

    def update_product(self, product, new_quantity):
       
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