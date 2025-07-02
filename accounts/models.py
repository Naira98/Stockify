from django.db import models
from django.contrib.auth.models import AbstractUser
from django_resized import ResizedImageField
# File: accounts/models.py

# This file defines the User model for the accounts app, extending Django's AbstractUser.
class User(AbstractUser):
    image = ResizedImageField(
        size=[300, 300],
        quality=75,
        upload_to='profile_images/',
        default='profile_images/default.jpg',
        blank=True,
        null=True
    )
    bio = models.TextField(blank=True, null=True)

    # The image field allows users to upload a profile image.
    


