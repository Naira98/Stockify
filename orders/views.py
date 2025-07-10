from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.views import View
# from .decorators import manager_required
from django.db import transaction
from .models import Order, OrderItem, Supermarket
from collections import defaultdict
from inventory.models import Product
from django.db.models import Count
from .forms import OrderForm, OrderItemForm
from .forms import SupermarketForm
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import CreateView, DeleteView, ListView, DetailView
from django.forms import inlineformset_factory
from django.contrib.admin.views.decorators import staff_member_required

# Create your views here.

