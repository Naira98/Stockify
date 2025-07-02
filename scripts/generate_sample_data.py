import os, sys, django, random

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
sys.path.append(PROJECT_ROOT)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "stockify.settings")
django.setup()


from inventory.models import (
    Category,
    Product,
    Factory,
    Supermarket,
)

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
    ("Fresh Mart", "New York", "123-456-7890"),
    ("Daily Needs", "Chicago", "987-654-3210"),
    ("Budget Basket", "Houston", "456-789-0123"),
]

for name, location, contact in supermarket_list:
    Supermarket.objects.get_or_create(name=name, location=location, contact=contact)

print("✅ Sample data created.")
