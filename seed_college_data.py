from decimal import Decimal

from django.contrib.auth import get_user_model

from shops.models import Category, Product, Shop, ShopCategory


User = get_user_model()

owners = [
    {
        "username": "zuzu_owner",
        "password": "zuzu@123",
        "email": "zuzu.owner@example.com",
        "phone": "9000000001",
        "address": "Near college campus",
        "shop_name": "Zuzu Zone",
        "shop_address": "College canteen lane",
        "shop_phone": "9001000001",
        "lat": "16.493554",
        "lng": "80.498228",
        "category": "Restaurant",
        "products": [
            ("Veg Fried Rice", "90.00", 40),
            ("Chicken Biryani", "150.00", 30),
            ("Paneer Noodles", "120.00", 25),
            ("Cold Coffee", "60.00", 50),
            ("Masala Dosa", "70.00", 35),
        ],
    },
    {
        "username": "lh2_owner",
        "password": "lh2@123",
        "email": "lh2.owner@example.com",
        "phone": "9000000002",
        "address": "Near LH2 block",
        "shop_name": "LH2 Shop",
        "shop_address": "Opposite LH2 block",
        "shop_phone": "9001000002",
        "lat": "16.492089",
        "lng": "80.497433",
        "category": "General Store",
        "products": [
            ("Mineral Water 1L", "20.00", 120),
            ("Lays Chips", "20.00", 90),
            ("Dairy Milk", "40.00", 80),
            ("Notebook A5", "35.00", 60),
            ("Pen", "10.00", 150),
        ],
    },
    {
        "username": "mh4_owner",
        "password": "mh4@123",
        "email": "mh4.owner@example.com",
        "phone": "9000000003",
        "address": "Near MH4 block",
        "shop_name": "MH4 Shop",
        "shop_address": "Ground floor, MH4 block",
        "shop_phone": "9001000003",
        "lat": "16.492030",
        "lng": "80.500645",
        "category": "General Store",
        "products": [
            ("Maggi Noodles", "18.00", 100),
            ("Biscuits Pack", "15.00", 110),
            ("Toothpaste", "55.00", 40),
            ("Soap", "35.00", 55),
            ("Soft Drink 750ml", "45.00", 70),
        ],
    },
    {
        "username": "rock_plaza_owner",
        "password": "rock@123",
        "email": "rock.owner@example.com",
        "phone": "9000000004",
        "address": "Rock Plaza corner",
        "shop_name": "Rock Plaza Stationery",
        "shop_address": "Rock Plaza, main entrance",
        "shop_phone": "9001000004",
        "lat": "16.494948",
        "lng": "80.498093",
        "category": "Stationery",
        "products": [
            ("A4 Notebook", "60.00", 100),
            ("Blue Pen", "12.00", 200),
            ("Practical Record", "85.00", 40),
            ("Stapler", "65.00", 30),
            ("Highlighter", "25.00", 75),
        ],
    },
]

created_users = 0
created_shops = 0
created_products = 0

for row in owners:
    user, user_created = User.objects.get_or_create(
        username=row["username"],
        defaults={
            "email": row["email"],
            "user_type": "shopkeeper",
            "phone": row["phone"],
            "address": row["address"],
        },
    )

    user.email = row["email"]
    user.user_type = "shopkeeper"
    user.phone = row["phone"]
    user.address = row["address"]
    user.set_password(row["password"])
    user.save()

    if user_created:
        created_users += 1

    category, _ = Category.objects.get_or_create(
        name=row["category"], defaults={"description": f"{row['category']} items"}
    )

    shop, shop_created = Shop.objects.get_or_create(
        name=row["shop_name"],
        defaults={
            "owner": user,
            "address": row["shop_address"],
            "phone": row["shop_phone"],
            "latitude": Decimal(row["lat"]),
            "longitude": Decimal(row["lng"]),
            "offers_delivery": True,
            "offers_pickup": True,
            "is_open": True,
        },
    )

    shop.owner = user
    shop.address = row["shop_address"]
    shop.phone = row["shop_phone"]
    shop.latitude = Decimal(row["lat"])
    shop.longitude = Decimal(row["lng"])
    shop.offers_delivery = True
    shop.offers_pickup = True
    shop.is_open = True
    shop.save()

    if shop_created:
        created_shops += 1

    ShopCategory.objects.get_or_create(shop=shop, category=category)

    for name, price, qty in row["products"]:
        product, product_created = Product.objects.get_or_create(
            shop=shop,
            name=name,
            defaults={
                "category": category,
                "price": Decimal(price),
                "description": f"{name} available at {shop.name}",
                "in_stock": True,
                "stock_quantity": qty,
            },
        )

        product.category = category
        product.price = Decimal(price)
        product.description = f"{name} available at {shop.name}"
        product.in_stock = True
        product.stock_quantity = qty
        product.save()

        if product_created:
            created_products += 1

print(
    f"Done. Users created: {created_users}, shops created: {created_shops}, products created: {created_products}"
)
print(f"Total shops now: {Shop.objects.count()}, total products now: {Product.objects.count()}")
