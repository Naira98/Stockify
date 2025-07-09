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
        """
        Add a product to the order or update quantity if it already exists
            
        Returns:
            tuple: (OrderItem instance, created_boolean)
            
        Raises:
            ValidationError: If quantity is invalid or insufficient stock for confirmed orders
        """          
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
   