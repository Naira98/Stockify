from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone

from stockify.models import TimestampModel
from inventory.models import Product, Factory
from accounts.models import User


class Shipment(TimestampModel):
    PENDING = "pending"
    LOADED = "loaded"
    RECEIVED = "received"

    STATUS_CHOICES = [
        (PENDING, "Pending"),
        (LOADED, "Loaded"),
        (RECEIVED, "Received"),
    ]

    factory = models.ForeignKey(Factory, on_delete=models.PROTECT)
    received_by = models.ForeignKey(
        User, on_delete=models.PROTECT, null=True, blank=True
    )
    received_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=PENDING)

    def confirm(self):
        if self.status == Shipment.PENDING:
            self.status = Shipment.LOADED
            self.save()

    def mark_as_received(self, user):
        if self.status == Shipment.LOADED:
            self.status = Shipment.RECEIVED
            self.received_by = user
            self.received_at = timezone.now()
            self.save()

    def is_loaded(self):
        return self.status == Shipment.LOADED

    def is_pending(self):
        return self.status == Shipment.PENDING

    def is_received(self):
        return self.status == Shipment.RECEIVED

    def __str__(self):
        return f"Shipment #{self.pk} from {self.factory.name}"


class ShipmentItem(models.Model):
    shipment = models.ForeignKey(
        Shipment,
        on_delete=models.CASCADE,
        related_name="items"
    )
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.quantity} of {self.product.name}"
