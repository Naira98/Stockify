from django.shortcuts import render
from django.views.generic import ListView
from django.db import models
from .models import Category, Product
from django.db.models import Q
from django.http import JsonResponse

class InventoryListView(ListView):
    model = Product
    template_name = 'inventory/inventory.html'
    context_object_name = 'products'
    
    def get_queryset(self):
        queryset = super().get_queryset()
        search_query = self.request.GET.get('search')
        category_id = self.request.GET.get('category')
        low_stock = self.request.GET.get('low_stock') == 'true'
        
        if search_query:
            queryset = queryset.filter(name__icontains=search_query)
        
        if category_id:
            queryset = queryset.filter(category__id=category_id)
        if low_stock:
            queryset = queryset.filter(quantity__lte=models.F('critical_amount'))
            
        return queryset.select_related('category')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['selected_category'] = self.request.GET.get('category', '')
        context['low_stock_filter'] = self.request.GET.get('low_stock') == 'true'
        context['current_search'] = self.request.GET.get('search', '')
        return context

    def render_to_response(self, context, **response_kwargs):
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            # AJAX request - return JSON
            products = list(context['products'].values(
                'id', 'name', 'quantity', 'critical_amount',
                category_name=models.F('category__name')
            ))
            return JsonResponse({'products': products})
        # Normal request - return HTML
        return super().render_to_response(context, **response_kwargs)