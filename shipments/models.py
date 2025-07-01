from django.db import models

from stockify.models import TimestampModel
from inventory.models import Product, Factory
from accounts.models import User


class Shipment(TimestampModel):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("loaded", "Loaded"),
        ("recieved", "Recieved"),
    ]

    factory = models.ForeignKey(Factory, on_delete=models.PROTECT)
    received_by = models.ForeignKey(User, on_delete=models.PROTECT)
    received_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)
    is_confirmed = models.BooleanField(default=False)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending",
    )

    def __str__(self):
        return f"Shipment #{self.pk} from {self.factory.name}"


class ShipmentItem(models.Model):
    shipment = models.ForeignKey(
        Shipment, related_name="items", on_delete=models.CASCADE
    )
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.IntegerField()

    def __str__(self):
        return f"{self.quantity} of {self.product.name}"
