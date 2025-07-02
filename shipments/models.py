from django.db import models
from django.utils import timezone

from stockify.models import TimestampModel
from inventory.models import Product, Factory
from accounts.models import User


class Shipment(TimestampModel):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("loaded", "Loaded"),
        ("recieved", "Received"),
    ]

    factory = models.ForeignKey(
        Factory, on_delete=models.PROTECT, null=False, blank=False
    )
    received_by = models.ForeignKey(
        User, on_delete=models.PROTECT, null=True, blank=True
    )
    received_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")

    def confirm(self):
        if self.status == "pending":
            self.status = "loaded"
            self.save()

    def mark_as_received(self, user):
        if self.status == "loaded":
            self.status = "recieved"
            self.received_by = user
            self.received_at = timezone.now()
            self.save()

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
