from django.db import models
from django.contrib.auth import get_user_model
from inventory.models import Product, Category
# Create your models here.

User = get_user_model()

class Supermarket(models.Model):
    """Supermarket model for customers"""
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=100)
    # location = models.CharField(max_length=255, help_text="E.g. Supermarket branch name or city")

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
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_orders')
    products = models.ManyToManyField(Product, through='OrderItem')