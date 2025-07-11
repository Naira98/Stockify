
from django.shortcuts import render,redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, DetailView,DeleteView,TemplateView,UpdateView
from django.db.models import Q, F
from inventory.forms import Addcategory, Addproduct,DeleteCategoryForm, ProductUpdateForm
from .models import Category, Product
from django.http import JsonResponse
from django.contrib import messages



from inventory import models

class InventoryListView(ListView):
    model = Product
    template_name = 'inventory/inventory.html'
    context_object_name = 'products'
    paginate_by = 6
    
    def get_queryset(self):
        queryset = super().get_queryset()
        search_query = self.request.GET.get('search')
        category_id = self.request.GET.get('category')
        low_stock = self.request.GET.get('low_stock') == 'true'
        out_of_stock = self.request.GET.get('out_of_stock') == 'true'

        # Apply filters
        if search_query:
            queryset = queryset.filter(name__icontains=search_query)
        
        if category_id:
            queryset = queryset.filter(category__id=category_id)
            
        if low_stock and out_of_stock:
            # Show products that are either low stock OR out of stock
            queryset = queryset.filter(
                Q(quantity=0) )
        elif low_stock:
            # Strict low stock filter (quantity > 0 AND <= critical)
            queryset = queryset.filter(
                quantity__gt=0, 
                quantity__lte=F('critical_amount'))
        elif out_of_stock:
            # Strict out of stock filter (quantity = 0)
            queryset = queryset.filter(quantity=0)
            
        return queryset.select_related('category')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['selected_category'] = self.request.GET.get('category', '')
        context['low_stock_filter'] = self.request.GET.get('low_stock') == 'true'
        context['out_of_stock_filter'] = self.request.GET.get('out_of_stock') == 'true'
        context['current_search'] = self.request.GET.get('search', '')
        return context

    def render_to_response(self, context, **response_kwargs):
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            products = list(context['products'].values(
                'id', 'name', 'quantity', 'critical_amount',
                category_name=F('category__name')
            ))
            return JsonResponse({'products': products})
        return super().render_to_response(context, **response_kwargs)

class Addcategoryview(CreateView):
    model = Category
    form_class = Addcategory
    template_name = 'inventory/add_category.html'
    success_url = reverse_lazy('inventory:inventory')

    def form_valid(self, form):
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Add New category'
        return context
    
class DeleteCategoryView(TemplateView):
    template_name = 'inventory/delete_category.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = DeleteCategoryForm()
        context['categories'] = Category.objects.all()
        return context
        
    def post(self, request, *args, **kwargs):
        form = DeleteCategoryForm(request.POST)
        if form.is_valid():
            category = form.cleaned_data['category']
            # Pass the category's ID (pk) instead of the object
            return redirect('inventory:deletecategoryconfirm', pk=category.id)
        return self.render_to_response(self.get_context_data(form=form))

class DeleteCategoryConfirmView(DeleteView):
    model = Category
    template_name = 'inventory/delete_category_confirm.html'
    success_url = reverse_lazy('inventory:inventory')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.get_object()
        return context
    
class AddProductView(CreateView):
    model = Product
    form_class = Addproduct
    template_name = 'inventory/add_product.html'
    success_url = reverse_lazy('inventory:inventory')

    def form_valid(self, form):
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Add New Product'
        return context

class Productdetailview(DetailView):
    model = Product
    template_name = 'inventory/details.html'
    context_object_name = 'product'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = self.get_object()
        context['is_low_stock'] = product.quantity > 0 and product.quantity <= product.critical_amount
        context['is_out_of_stock'] = product.quantity == 0
        return context
class ProductDeleteView(DeleteView):
    model = Product
    template_name ='inventory/delete_product.html'  
    success_url = reverse_lazy('inventory:inventory') 




class ProductUpdateView(UpdateView):
    model = Product
    form_class = ProductUpdateForm
    template_name = 'inventory/edit_product.html'
    success_url = reverse_lazy('inventory:inventory')
    
    def form_valid(self, form):
        # Get the product instance
        product = form.instance
        
        # Handle image upload if new image was provided
        if 'image' in self.request.FILES:
            new_image = self.request.FILES['image']
            
            # Delete old image if it exists (except default)
            if product.image and not product.image.name.endswith('default.png'):
                # Delete the file from storage
                storage, path = product.image.storage, product.image.path
                storage.delete(path)
            
            # Assign and save the new image
            product.image = new_image
        
        # Save the product with all changes
        product.save()
        
        messages.success(self.request, f'Product "{product.name}" updated successfully!')
        return super().form_valid(form)
