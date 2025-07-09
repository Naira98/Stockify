from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Submit
from .models import Order, OrderItem, Supermarket


class SupermarketForm(forms.ModelForm):
    class Meta:
        model = Supermarket
        fields = ["name", "location"]