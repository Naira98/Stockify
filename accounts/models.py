from django.db import models
from django.contrib.auth.models import AbstractUser


# Create your models here.

class CustomerUser(AbstractUser):
    image = models.ImageField(upload_to='profile_pics', default='default.jpg', blank=True)
    def __str__(self):
        return f"{self.username} ({self.email})"