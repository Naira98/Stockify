from django.db import models


# Create your models here.

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