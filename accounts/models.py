from django.db import models
from django.contrib.auth.models import AbstractUser
# File: accounts/models.py

# This file defines the User model for the accounts app, extending Django's AbstractUser.
class User(AbstractUser):
    
    image = models.ImageField(upload_to='profile_images/', default='default.jpg', blank=True, null=True)
    # The image field allows users to upload a profile image.
    
    