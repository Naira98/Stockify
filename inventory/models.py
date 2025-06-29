from django.db import models
from stockify.models import TimestampModel


class Product(TimestampModel):
    name = models.CharField(
        max_length=255,
        null=False,
        blank=False,
        unique=True,
    )
    description = models.TextField(
        null=True,
        blank=True,
    )
    quantity = models.PositiveIntegerField(
        null=False,
        blank=False,
    )
    critical_amount = models.PositiveIntegerField(
        null=False,
        blank=False,
        default=10,
    )
    sku = models.CharField(
        max_length=50,
        unique=True,
        null=True,
        blank=True,
        help_text="Stock Keeping Unit (optional)",
    )

    def __str__(self):
        return f"{self.name} (ID: {self.pk})"

    def is_low_stock(self):
        return self.quantity < self.critical_amount



class Factory(TimestampModel):
    name = models.CharField(
        max_length=255,
        null=False,
        blank=False,
        unique=True,
    )
    location = models.CharField(
        max_length=255,
        null=False,
        blank=False,
    )
    contact = models.CharField(
        max_length=255,
        null=False,
        blank=False,
    )

    def __str__(self):
        return f"{self.name} | {self.location}"

    class Meta(TimestampModel.Meta):
        verbose_name_plural = "Factories"



class Supermarket(TimestampModel):
    name = models.CharField(
        max_length=255,
        null=False,
        blank=False,
        unique=True,
    )
    location = models.CharField(
        max_length=255,
        null=False,
        blank=False,
    )
    contact = models.CharField(
        max_length=255,
        null=False,
        blank=False,
    )

    def __str__(self):
        return f"{self.name} | {self.location}"
