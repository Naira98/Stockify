from django.db import models
from stockify.models import TimestampModel

class TimestampModel(models.Model):
    """
    An abstract base class model that provides self-updating
    'created_at' and 'updated_at' fields.
    """
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        
class Category(TimestampModel):
    name = models.CharField(
        max_length=255,
        null=False,
        blank=False,
        unique=True,
    )
    class Meta(TimestampModel.Meta):
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name


class Product(TimestampModel):
    name = models.CharField(
        max_length=255,
        null=False,
        blank=False,
        unique=True,
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        null=False,
        blank=False,
        related_name="products",
    )
    description = models.TextField(
        null=True,
        blank=True,
    )
    critical_amount = models.PositiveIntegerField(
        null=False,
        blank=False,
        default=10,
    )
    quantity = models.PositiveIntegerField(
        null=False,
        blank=False,
    )
    image = models.ImageField(
        upload_to="products/",
        null=False,
        blank=False,
    )

    def __str__(self):
        return f"{self.name}"

    def is_low_stock(self):
        return self.quantity <= self.critical_amount

    def is_out_of_stock(self):
        return self.quantity == 0
    