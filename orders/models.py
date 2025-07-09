from django.db import models
from accounts.models import User
from inventory.models import Product, Category
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.db import transaction
from stockify.models import TimestampModel


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
        if quantity > product.quantity:
            return f"Limited stock: only {product.quantity} units left."

        order = OrderItem.objects.filter(order=self, product=product).first()

        if not order:
            order = OrderItem(order=self, product=product, quantity=0)
            order.save()
            created = True
        else:
            created = False
   