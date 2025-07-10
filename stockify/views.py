from collections import defaultdict
from django.db.models.functions import TruncDay
from django.db.models import Count, F
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.decorators import login_required
from inventory.models import Product, Category
from shipments.models import Shipment
from orders.models import Order
import json
from django.utils import timezone
from django.db.models import F
from django.shortcuts import render


@login_required
def dashboard(request):
    try:
        days = int(request.GET.get("days", 7))
        if days not in [7, 30, 90]:
            days = 7
    except ValueError:
        days = 7

    date_threshold = timezone.now() - timedelta(days=days - 1)

    # Fetch shipment data grouped by day
    shipment_data_raw = (
        Shipment.objects.filter(created_at__date__gte=date_threshold.date())
        .annotate(day=TruncDay("created_at"))
        .values("day")
        .annotate(count=Count("id"))
    )

    # Fetch order data grouped by day
    order_data_raw = (
        Order.objects.filter(created_at__date__gte=date_threshold.date())
        .annotate(day=TruncDay("created_at"))
        .values("day")
        .annotate(count=Count("id"))
    )

    # Merge both datasets by day
    data_by_day = defaultdict(lambda: {"orders": 0, "shipments": 0})

    for entry in shipment_data_raw:
        data_by_day[entry["day"].date()]["shipments"] = entry["count"]

    for entry in order_data_raw:
        data_by_day[entry["day"].date()]["orders"] = entry["count"]

    # Sort by date
    sorted_days = sorted(data_by_day.keys())
    combined_labels = [day.strftime("%b %d") for day in sorted_days]
    combined_orders = [data_by_day[day]["orders"] for day in sorted_days]
    combined_shipments = [data_by_day[day]["shipments"] for day in sorted_days]

    category_labels = list(Category.objects.values_list("name", flat=True))
    category_data = [
        Product.objects.filter(category=cat).count() for cat in Category.objects.all()
    ]

    total_products = Product.objects.count()
    low_stock_products = Product.objects.filter(
        quantity__gt=0, quantity__lte=F("critical_amount")
    ).count()
    zero_stock_products = Product.objects.filter(quantity=0).count()
    total_categories = Category.objects.count()
    
    context = {
        "selected_days": days,
        "category_labels": json.dumps(category_labels),
        "category_data": json.dumps(category_data),
        "chart_labels": json.dumps(combined_labels),
        "order_data": json.dumps(combined_orders),
        "shipment_data": json.dumps(combined_shipments),
        "total_products": total_products,
        "low_stock_products": low_stock_products,
        "zero_stock_products": zero_stock_products,
        "total_categories": total_categories,
    }

    return render(request, "dashboard/dashboard.html", context)
