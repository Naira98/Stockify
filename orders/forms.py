from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Submit
from .models import Order, OrderItem, Supermarket


class SupermarketForm(forms.ModelForm):
    class Meta:
        model = Supermarket
        fields = ["name", "location"]
        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class": "border border-gray-300 rounded px-3 py-2 w-full focus:outline-none focus:ring-2 focus:ring-blue-500"
                }
            ),
             "location": forms.Textarea(
                attrs={
                    "class": "border border-gray-300 rounded px-3 py-2 w-full focus:outline-none focus:ring-2 focus:ring-blue-500",
                    "rows": 3,
                }
            ),
        }

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ["supermarket"]    
        widgets = {
            "supermarket": forms.Select(
                attrs={
                    "class": "border border-gray-300 rounded px-3 py-2 w-full focus:outline-none focus:ring-2 focus:ring-blue-500"
                }
            ),
        }

class OrderItemForm(forms.ModelForm):
    class Meta:
        model = OrderItem
        fields = ["product", "quantity"]       
        widgets = {
            "product": forms.Select(
                attrs={
                    "class": "border border-gray-300 rounded px-3 py-2 w-full focus:outline-none focus:ring-2 focus:ring-blue-500"
                }
            ),    
            "quantity": forms.NumberInput(
                attrs={
                    "class": "border border-gray-300 rounded px-3 py-2 w-full focus:outline-none focus:ring-2 focus:ring-blue-500",
                    "min": "1",
                }
            ),
        }
