from django.db import models
from django.contrib.auth.models import AbstractUser
# File: accounts/models.py

# This file defines the User model for the accounts app, extending Django's AbstractUser.
class User(AbstractUser):

    ROLE_CHOICES = [
        ('employee', 'Employee'),
        ('manager', 'Manager'),
    ]
    
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='employee')