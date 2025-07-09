from django.db import models
from django.utils import timezone


class TimestampModel(models.Model):
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    class Meta:
        abstract = True
        ordering = ["-created_at"]

    def save(self, *args, **kwargs):
        if not kwargs.pop("manual_update", False):
            self.updated_at = timezone.now()
        super().save(*args, **kwargs)
