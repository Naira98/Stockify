from django.db import models
from django.contrib.auth import get_user_model
from inventory.models import Product, Category
from django.utils import timezone
from django.core.exceptions import ValidationError
# from accounts.models import User

# Create your models here.

User = get_user_model()

class Supermarket(models.Model):
    """Supermarket model for customers"""
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=100)
    # location = models.CharField(max_length=100, help_text="E.g. Supermarket branch name or city")

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
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_orders')
    confirmed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='confirmed_orders')
    products = models.ManyToManyField(Product, through='OrderItem')
    notes = models.TextField(blank=True)

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
        """
        Add a product to the order or update quantity if it already exists
            
        Returns:
            tuple: (OrderItem instance, created_boolean)
            
        Raises:
            ValidationError: If quantity is invalid or insufficient stock for confirmed orders
        """          
        if quantity <= 0:
            raise ValidationError("Quantity must be greater than 0")     

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
            # Product already exists, update quantity
            old_quantity = order_item.quantity
            order_item.quantity += quantity
            order_item.save()    

            if self.status == 'confirmed':
                # Check if we have enough stock for the additional quantity
                if product.current_quantity < quantity:
                    # Rollback the quantity change
                    order_item.quantity = old_quantity
                    order_item.save()
                    raise ValidationError(
                        f"Insufficient stock to add {quantity} more {product.name}. "
                        f"Available: {product.current_quantity}"
                    )
                product.current_quantity -= quantity
                product.save()
        else:
            # New product added, update inventory if order is confirmed
            if self.status == 'confirmed':
                product.current_quantity -= quantity
                product.save()
        
        return order_item, created
                
         