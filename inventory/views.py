from django.shortcuts import render,redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, DetailView,DeleteView,TemplateView
from django.db.models import Q, F
from inventory.forms import Addcategory, Addproduct,DeleteCategoryForm
from .models import Category, Product
from django.http import JsonResponse

from inventory import models

class InventoryListView(ListView):
    model = Product
    template_name = 'inventory/inventory.html'
    context_object_name = 'products'
    paginate_by = 3
    
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
                category_name=models.F('category__name')
            ))
            return JsonResponse({'products': products})
        return super().render_to_response(context, **response_kwargs)

