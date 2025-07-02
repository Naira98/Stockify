from django import forms
from inventory.models import Factory
from .models import Shipment


class ShipmentForm(forms.ModelForm):
    class Meta:
        model = Shipment
        fields = ["factory"]
        widgets = {
            "factory": forms.Select(
                attrs={
                    "class": (
                        "block w-full mt-1 text-base py-3 px-4 pr-12 "
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
                        "block w-full mt-1 text-base py-3 px-4 "
                        "border border-gray-300 rounded-md shadow-sm "
                        "focus:ring-indigo-500 focus:border-indigo-500"
                    )
                }
            ),
            "location": forms.TextInput(
                attrs={
                    "class": (
                        "block w-full mt-1 text-base py-3 px-4 "
                        "border border-gray-300 rounded-md shadow-sm "
                        "focus:ring-indigo-500 focus:border-indigo-500"
                    )
                }
            ),
        }
