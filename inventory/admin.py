from django.contrib import admin

# Register your models here.
from .models import Category, Product,Supermarket,Factory

admin.site.register(Category)
admin.site.register(Product)
admin.site.register(Supermarket)
admin.site.register(Factory)


