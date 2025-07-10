import os, sys, django, random
from datetime import timedelta
from django.utils import timezone

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
sys.path.append(PROJECT_ROOT)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "stockify.settings")
django.setup()

from inventory.models import Category, Product
from accounts.models import User
from shipments.models import Factory, Shipment, ShipmentItem
from orders.models import Supermarket, Order, OrderItem

# Categories
category_names = ["Beverages", "Snacks", "Dairy", "Produce", "Bakery"]
categories = []

for name in category_names:
    category, _ = Category.objects.get_or_create(name=name)
    categories.append(category)

# Products
product_names = [
    {
        "name": "V-Cola",
        "category": "Beverages",
        "description": "Delicious soda",
        "quantity": random.randint(0, 50),
        "critical_amount": 10,
        "image": "/products/v-cola.png",
    },
    {
        "name": "Big Chips",
        "category": "Snacks",
        "description": "Crunchy chips",
        "quantity": random.randint(0, 50),
        "critical_amount": 10,
        "image": "/products/big-chips.png",
    },
    {
        "name": "Milk",
        "category": "Dairy",
        "description": "Fresh milk",
        "quantity": random.randint(0, 50),
        "critical_amount": 10,
        "image": "/products/milk.png",
    },
    {
        "name": "Bananas",
        "category": "Produce",
        "description": "Fresh bananas",
        "quantity": random.randint(0, 50),
        "critical_amount": 10,
        "image": "/products/bananas.png",
    },
    {
        "name": "Bread",
        "category": "Bakery",
        "description": "Fresh bread",
        "quantity": random.randint(0, 50),
        "critical_amount": 10,
        "image": "/products/bread.png",
    },
    {
        "name": "Yogurt",
        "category": "Dairy",
        "description": "Fresh yogurt",
        "quantity": random.randint(0, 50),
        "critical_amount": 10,
        "image": "/products/yogurt.png",
    },
    {
        "name": "Orange Juice",
        "category": "Beverages",
        "description": "Fresh orange juice",
        "quantity": random.randint(0, 50),
        "critical_amount": 10,
        "image": "/products/orange-juice.png",
    },
    {
        "name": "Cookies",
        "category": "Snacks",
        "description": "Delicious cookies",
        "quantity": random.randint(0, 50),
        "critical_amount": 10,
        "image": "/products/cookies.png",
    },
    {
        "name": "Sparkle Water",
        "category": "Beverages",
        "description": "Refreshing sparkling water",
        "quantity": random.randint(0, 50),
        "critical_amount": 10,
        "image": "/products/sparkle-water.png",
    },
    {
        "name": "Cheddar Bites",
        "category": "Snacks",
        "description": "Cheesy snack bites",
        "quantity": random.randint(0, 50),
        "critical_amount": 10,
        "image": "/products/cheddar-bites.png",
    },
    {
        "name": "Cheese",
        "category": "Dairy",
        "description": "Sliced cheese pack",
        "quantity": random.randint(0, 50),
        "critical_amount": 10,
        "image": "/products/cheese.png",
    },
    {
        "name": "Lettuce",
        "category": "Produce",
        "description": "Crisp lettuce head",
        "quantity": random.randint(0, 50),
        "critical_amount": 10,
        "image": "/products/lettuce.png",
    },
    {
        "name": "Baguette",
        "category": "Bakery",
        "description": "Classic French baguette",
        "quantity": random.randint(0, 50),
        "critical_amount": 10,
        "image": "/products/baguette.png",
    },
    {
        "name": "Butter Croissant",
        "category": "Bakery",
        "description": "Buttery soft croissant",
        "quantity": random.randint(0, 50),
        "critical_amount": 10,
        "image": "/products/butter-croissant.png",
    },
    {
        "name": "Apple Juice",
        "category": "Beverages",
        "description": "Pure apple juice",
        "quantity": random.randint(0, 50),
        "critical_amount": 10,
        "image": "/products/apple-juice.png",
    },
    {
        "name": "Trail Mix",
        "category": "Snacks",
        "description": "Healthy nuts and dried fruits mix",
        "quantity": random.randint(0, 50),
        "critical_amount": 10,
        "image": "/products/trail-mix.png",
    },
    {
        "name": "Strawberries",
        "category": "Produce",
        "description": "Fresh ripe strawberries",
        "quantity": random.randint(0, 50),
        "critical_amount": 10,
        "image": "/products/strawberries.png",
    },
    {
        "name": "Cream Cheese",
        "category": "Dairy",
        "description": "Smooth cream cheese spread",
        "quantity": random.randint(0, 50),
        "critical_amount": 10,
        "image": "/products/cream-cheese.png",
    },
]

for product in product_names:
    name = product["name"]
    cat_name = product["category"]
    description = product["description"]
    quantity = product["quantity"]
    critical_amount = product["critical_amount"]
    image_path = product["image"]

    category = Category.objects.get(name=cat_name)

    Product.objects.get_or_create(
        name=name,
        category=category,
        defaults={
            "description": description,
            "quantity": quantity,
            "critical_amount": critical_amount,
            "image": image_path,
        },
    )


# Factories
factory_list = [
    ("Sunshine Foods", "New York"),
    ("Global Beverages", "Los Angeles"),
    ("Farm Fresh", "Texas"),
]

for name, location in factory_list:
    Factory.objects.get_or_create(name=name, location=location)

# Supermarkets
supermarket_list = [
    ("Fresh Mart", "New York"),
    ("Daily Needs", "Chicago"),
    ("Budget Basket", "Houston"),
]

for name, location in supermarket_list:
    Supermarket.objects.get_or_create(name=name, location=location)


def random_date_within(days):
    now = timezone.now()
    delta = timedelta(days=random.randint(0, days))
    return now - delta


# Shipments
factories = Factory.objects.all()
products = list(Product.objects.all())
staff_users = User.objects.filter(is_staff=True)

for _ in range(15):
    factory = random.choice(factories)
    shipment_date = random_date_within(90)
    shipment = Shipment.objects.create(
        factory=factory,
        created_at=shipment_date,
        updated_at=shipment_date,
        status=random.choice([Shipment.PENDING, Shipment.LOADED, Shipment.RECEIVED]),
    )

    # Add shipment items
    for _ in range(random.randint(1, 4)):
        product = random.choice(products)
        quantity = random.randint(5, 20)
        ShipmentItem.objects.create(
            shipment=shipment,
            product=product,
            quantity=quantity,
        )

    # Optionally mark received
    if shipment.status == Shipment.RECEIVED and staff_users.exists():
        user = random.choice(staff_users)
        shipment.received_by = user
        shipment.received_at = shipment_date + timedelta(hours=3)
        shipment.save()


# Orders
supermarkets = list(Supermarket.objects.all())
users = list(User.objects.all())
products = list(Product.objects.all())

if not supermarkets or not users or not products:
    print("❌ Make sure there are supermarkets, users, and products in the database.")
    exit()

for _ in range(15):
    supermarket = random.choice(supermarkets)
    created_by = random.choice(users)
    created_at = random_date_within(90)
    status = random.choice(["pending", "confirmed", "delivered"])

    order = Order.objects.create(
        supermarket=supermarket,
        created_by=created_by,
        status=status,
        created_at=created_at,
        updated_at=created_at,
    )

    if status in ["confirmed", "delivered"]:
        order.confirmed_by = random.choice(users)
        order.delivery_date = created_at + timedelta(days=random.randint(1, 5))
        order.save()

    # Add 1–4 products to order
    selected_products = random.sample(products, k=random.randint(1, 4))
    for product in selected_products:
        quantity = random.randint(1, min(product.quantity or 10, 5))
        OrderItem.objects.create(
            order=order,
            product=product,
            quantity=quantity
        )

print("✅ Sample data created.")
