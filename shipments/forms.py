from django import forms
from typing import cast
from django.forms import ModelChoiceField
from inventory.models import Factory, Product, Category
from .models import Shipment, ShipmentItem


class ShipmentForm(forms.ModelForm):
    class Meta:
        model = Shipment
        fields = ["factory"]
        widgets = {
            "factory": forms.Select(
                attrs={
                    "class": (
                        "block w-full mt-1 text-base py-3 px-2 "
                        "border border-gray-300 rounded-md shadow-sm "
                        "focus:ring-indigo-500 focus:border-indigo-500"
                    )
                }
            ),
        }


class FactoryForm(forms.ModelForm):
    class Meta:
        model = Factory
        fields = ["name", "location"]
        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class": (
                        "block w-full mt-1 text-base py-3 px-2  "
                        "border border-gray-300 rounded-md shadow-sm "
                        "focus:ring-indigo-500 focus:border-indigo-500"
                    )
                }
            ),
            "location": forms.TextInput(
                attrs={
                    "class": (
                        "block w-full mt-1 text-base py-3 px-2 "
                        "border border-gray-300 rounded-md shadow-sm "
                        "focus:ring-indigo-500 focus:border-indigo-500"
                    )
                }
            ),
        }


class AddShipmentItemForm(forms.ModelForm):
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        required=False,
        label="Category",
        widget=forms.Select(
            attrs={
                "class": (
                    "block w-full mt-1 text-base py-3 px-2 "
                    "border border-gray-300 rounded-md shadow-sm "
                    "focus:ring-indigo-500 focus:border-indigo-500"
                )
            }
        ),
    )

    class Meta:
        model = ShipmentItem
        fields = ["category", "product", "quantity"]
        widgets = {
            "product": forms.Select(
                attrs={
                    "class": (
                        "block w-full mt-1 text-base py-3 px-2 "
                        "border border-gray-300 rounded-md shadow-sm "
                        "focus:ring-indigo-500 focus:border-indigo-500"
                    )
                }
            ),
            "quantity": forms.NumberInput(
                attrs={
                    "class": (
                        "block w-full mt-1 text-base py-3 px-2 "
                        "border border-gray-300 rounded-md shadow-sm "
                        "focus:ring-indigo-500 focus:border-indigo-500"
                    )
                }
            ),
        }
