#!/usr/bin/env python
import os
import django
import sys

# Add the project directory to the Python path
sys.path.append('/Users/sushank/Documents/GitHub/market-nearby')

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'market_nearby.settings')
django.setup()

from accounts.models import User
from shops.models import Shop, Category, Product, ShopCategory
from decimal import Decimal

# Create superuser
if not User.objects.filter(username='admin').exists():
    admin_user = User.objects.create_user(
        username='admin',
        email='admin@marketnearby.com',
        password='admin123',
        user_type='admin',
        is_staff=True,
        is_superuser=True
    )
    print("Created admin user: admin / admin123")

# Create sample shopkeeper
if not User.objects.filter(username='shopkeeper1').exists():
    shopkeeper = User.objects.create_user(
        username='shopkeeper1',
        email='shop@example.com',
        password='shop123',
        user_type='shopkeeper',
        phone='+91 98765 43210'
    )
    print("Created shopkeeper: shopkeeper1 / shop123")

# Create sample customer
if not User.objects.filter(username='customer1').exists():
    customer = User.objects.create_user(
        username='customer1',
        email='customer@example.com',
        password='customer123',
        user_type='customer',
        phone='+91 98765 43211'
    )
    print("Created customer: customer1 / customer123")

# Create categories
categories_data = [
    {'name': 'Vegetables', 'description': 'Fresh vegetables and greens'},
    {'name': 'Fruits', 'description': 'Fresh seasonal fruits'},
    {'name': 'Bakery', 'description': 'Bread, cakes, and pastries'},
    {'name': 'Dairy', 'description': 'Milk, cheese, and dairy products'},
    {'name': 'Groceries', 'description': 'Essential grocery items'},
    {'name': 'Organic', 'description': 'Organic and natural products'},
    {'name': 'Snacks', 'description': 'Snacks and quick bites'},
]

for cat_data in categories_data:
    category, created = Category.objects.get_or_create(
        name=cat_data['name'],
        defaults={'description': cat_data['description']}
    )
    if created:
        print(f"Created category: {category.name}")

# Get users and categories
shopkeeper = User.objects.get(username='shopkeeper1')
vegetables_cat = Category.objects.get(name='Vegetables')
fruits_cat = Category.objects.get(name='Fruits')
bakery_cat = Category.objects.get(name='Bakery')
dairy_cat = Category.objects.get(name='Dairy')
groceries_cat = Category.objects.get(name='Groceries')
organic_cat = Category.objects.get(name='Organic')

# Create sample shops
shops_data = [
    {
        'name': 'Green Valley Vegetables',
        'address': '123 Market Street, Downtown',
        'phone': '+91 98765 43210',
        'is_open': True,
        'rating': Decimal('4.5'),
        'categories': [vegetables_cat, fruits_cat, organic_cat]
    },
    {
        'name': 'Fresh Daily Market',
        'address': '456 Garden Road, Central',
        'phone': '+91 98765 43211',
        'is_open': True,
        'rating': Decimal('4.3'),
        'categories': [groceries_cat, dairy_cat]
    },
    {
        'name': 'Golden Bakery',
        'address': '789 Bread Lane, Old Town',
        'phone': '+91 98765 43212',
        'is_open': False,
        'rating': Decimal('4.7'),
        'categories': [bakery_cat]
    }
]

for shop_data in shops_data:
    categories = shop_data.pop('categories')
    shop, created = Shop.objects.get_or_create(
        name=shop_data['name'],
        defaults={**shop_data, 'owner': shopkeeper}
    )
    if created:
        print(f"Created shop: {shop.name}")
        # Add categories
        for category in categories:
            ShopCategory.objects.get_or_create(shop=shop, category=category)

# Create sample products
products_data = [
    {
        'name': 'Fresh Organic Tomatoes',
        'shop_name': 'Green Valley Vegetables',
        'category': vegetables_cat,
        'price': Decimal('45.00'),
        'original_price': Decimal('60.00'),
        'in_stock': True,
        'stock_quantity': 50,
        'rating': Decimal('4.5'),
        'description': 'Fresh organic tomatoes grown locally'
    },
    {
        'name': 'Artisan Sourdough Bread',
        'shop_name': 'Golden Bakery',
        'category': bakery_cat,
        'price': Decimal('120.00'),
        'in_stock': True,
        'stock_quantity': 20,
        'rating': Decimal('4.8'),
        'description': 'Handcrafted sourdough bread baked fresh daily'
    },
    {
        'name': 'Fresh Dairy Milk',
        'shop_name': 'Fresh Daily Market',
        'category': dairy_cat,
        'price': Decimal('55.00'),
        'in_stock': False,
        'stock_quantity': 0,
        'rating': Decimal('4.2'),
        'description': 'Pure fresh milk from local dairy farm'
    },
    {
        'name': 'Organic Baby Spinach',
        'shop_name': 'Green Valley Vegetables',
        'category': vegetables_cat,
        'price': Decimal('35.00'),
        'original_price': Decimal('45.00'),
        'in_stock': True,
        'stock_quantity': 30,
        'rating': Decimal('4.6'),
        'description': 'Tender organic baby spinach leaves'
    }
]

for product_data in products_data:
    shop_name = product_data.pop('shop_name')
    shop = Shop.objects.get(name=shop_name)
    
    product, created = Product.objects.get_or_create(
        name=product_data['name'],
        shop=shop,
        defaults={**product_data}
    )
    if created:
        print(f"Created product: {product.name}")

print("Sample data created successfully!")
print("\nLogin credentials:")
print("Admin: admin / admin123")
print("Shopkeeper: shopkeeper1 / shop123")
print("Customer: customer1 / customer123")
