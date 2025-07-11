from django.db import models
from stockify.models import TimestampModel
  
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
     
    image = models.ImageField(
        upload_to="products/",
        null=True,  # Changed from False to True
        blank=True,  # Changed from False to True
        default='products/default.png'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    def save(self, *args, **kwargs):
        # Handle image changes on save
        if self.pk:  # Only for existing instances
            try:
                old = Product.objects.get(pk=self.pk)
                if old.image and old.image != self.image:
                    old.image.delete(save=False)
            except Product.DoesNotExist:
                pass
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name}"

    def is_low_stock(self):
        return self.quantity <= self.critical_amount

    def is_out_of_stock(self):
        return self.quantity == 0
    