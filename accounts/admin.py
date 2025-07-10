# admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'role', 'date_joined', 'last_login')
    search_fields = ('username', 'email')
    readonly_fields = ('date_joined', 'last_login')
    
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal Information', {'fields': ('email', 'image', 'bio')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'is_user')}),
        ('Important Dates', {'fields': ('last_login', 'date_joined')}),
    )
    
    def role(self, obj):
        if obj.is_superuser:
            return "Admin"
        elif obj.is_user:
            return "Employee"
        return "User"
    role.short_description = 'Role'

admin.site.register(User, CustomUserAdmin)