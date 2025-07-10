from django import forms
from inventory.models import Category
from .models import Factory, Shipment, ShipmentItem
from django.core.exceptions import ValidationError
from .models import Factory


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


class ShipmentFilterForm(forms.Form):
    factory = forms.ModelChoiceField(
        queryset=Factory.objects.all(),
        required=False,
        label="Factory",
        widget=forms.Select(
            attrs={
                "class": "px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500",
                "onchange": "this.form.submit()",
            }
        ),
    )


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
                    ),
                }
            ),
        }

    def clean_quantity(self):
        quantity = self.cleaned_data.get("quantity")

        if quantity is not None and quantity < 1:
            raise ValidationError("Quantity must be at least 1.")

        return quantity


class EditShipmentItemForm(forms.ModelForm):
    class Meta:
        model = ShipmentItem
        fields = ["quantity"]
        widgets = {
            "quantity": forms.NumberInput(
                attrs={
                    "class": (
                        "block w-full mt-1 text-base py-3 px-2 "
                        "border border-gray-300 rounded-md shadow-sm "
                        "focus:ring-indigo-500 focus:border-indigo-500"
                    ),
                }
            ),
        }

    def clean_quantity(self):
        quantity = self.cleaned_data.get("quantity")

        if quantity and quantity < 1:
            raise ValidationError("Quantity must be at least 1.")

        return quantity
