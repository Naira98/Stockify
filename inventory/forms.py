from django import forms
from .models import Category, Product

class Addproduct(forms.ModelForm):
    class Meta:
        model = Product
        fields = ('name', 'category', 'description', 'quantity', 'image') 

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            if field != 'image':
                self.fields[field].widget.attrs.update({
                    'class': 'block w-full mt-1 text-base py-3 px-2 border border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500'
                })
        
        # Special handling for specific fields
        self.fields['description'].widget.attrs.update({
            'rows': '3',
            'placeholder': 'Enter product description...',
            'class': 'block w-full mt-1 text-base py-3 px-2 border border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500'
        })
        self.fields['image'].widget.attrs.update({
            'class': 'block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-semibold file:bg-indigo-50 file:text-indigo-700 hover:file:bg-indigo-100'
        })


class Addcategory(forms.ModelForm):
    class Meta:
        model = Category
        fields = '__all__'
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({
                'class': 'block w-full mt-1 text-base py-3 px-2 border border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500'
            })


class DeleteCategoryForm(forms.Form):
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        label="Select Category to Delete",
        widget=forms.Select(attrs={
            'class': 'block w-full mt-1 text-base py-3 px-2 border border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500'
        })
    )        

    
class ProductUpdateForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = '__all__'
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Exclude timestamp fields from styling
        editable_fields = [f for f in self.fields if f not in ['created_at', 'updated_at', 'image']]
        
        for field in editable_fields:
            self.fields[field].widget.attrs.update({
                'class': 'block w-full mt-1 text-base py-3 px-2 border border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500'
            })
        
        # Special handling for specific fields
        self.fields['description'].widget.attrs.update({
            'rows': '3',
            'placeholder': 'Enter product description...',
            'class': 'block w-full mt-1 text-base py-3 px-2 border border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500'
        })
        self.fields['image'].widget.attrs.update({
            'class': 'block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-semibold file:bg-indigo-50 file:text-indigo-700 hover:file:bg-indigo-100'
        })