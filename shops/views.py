from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Shop, Product, Category

def index(request):
    """Main page showing shops and products"""
    # Get featured shops
    shops = Shop.objects.select_related('owner').prefetch_related('categories__category').all()[:6]
    
    # Get featured products
    products = Product.objects.select_related('shop', 'category').all()[:8]
    
    # Get categories
    categories = Category.objects.all()
    
    # Get search query
    search_query = request.GET.get('search', '')
    location = request.GET.get('location', '')
    
    context = {
        'shops': shops,
        'products': products,
        'categories': categories,
        'search_query': search_query,
        'location': location,
    }
    
    return render(request, 'shops/index.html', context)

def shop_list(request):
    """List all shops with filtering and searching"""
    shops = Shop.objects.select_related('owner').prefetch_related('categories__category')
    
    # Search functionality
    search_query = request.GET.get('search', '')
    category_id = request.GET.get('category', '')
    location = request.GET.get('location', '')
    
    if search_query:
        shops = shops.filter(
            Q(name__icontains=search_query) |
            Q(address__icontains=search_query) |
            Q(categories__category__name__icontains=search_query)
        ).distinct()
    
    if category_id:
        shops = shops.filter(categories__category_id=category_id)
    
    # Pagination
    paginator = Paginator(shops, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    categories = Category.objects.all()
    
    context = {
        'page_obj': page_obj,
        'categories': categories,
        'search_query': search_query,
        'selected_category': category_id,
        'location': location,
    }
    
    return render(request, 'shops/shop_list.html', context)

def shop_detail(request, pk):
    """Detailed view of a shop"""
    shop = get_object_or_404(Shop, pk=pk)
    products = Product.objects.filter(shop=shop).select_related('category')
    reviews = shop.reviews.select_related('user').all()[:10]
    
    context = {
        'shop': shop,
        'products': products,
        'reviews': reviews,
    }
    
    return render(request, 'shops/shop_detail.html', context)

def product_list(request):
    """List all products with filtering and searching"""
    products = Product.objects.select_related('shop', 'category')
    
    # Search functionality
    search_query = request.GET.get('search', '')
    category_id = request.GET.get('category', '')
    shop_id = request.GET.get('shop', '')
    in_stock_only = request.GET.get('in_stock', '') == 'true'
    
    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    
    if category_id:
        products = products.filter(category_id=category_id)
    
    if shop_id:
        products = products.filter(shop_id=shop_id)
    
    if in_stock_only:
        products = products.filter(in_stock=True)
    
    # Pagination
    paginator = Paginator(products, 16)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    categories = Category.objects.all()
    shops = Shop.objects.all()
    
    context = {
        'page_obj': page_obj,
        'categories': categories,
        'shops': shops,
        'search_query': search_query,
        'selected_category': category_id,
        'selected_shop': shop_id,
        'in_stock_only': in_stock_only,
    }
    
    return render(request, 'shops/product_list.html', context)

def product_detail(request, pk):
    """Detailed view of a product"""
    product = get_object_or_404(Product, pk=pk)
    reviews = product.reviews.select_related('user').all()[:10]
    related_products = Product.objects.filter(
        category=product.category
    ).exclude(pk=product.pk)[:4]
    
    context = {
        'product': product,
        'reviews': reviews,
        'related_products': related_products,
    }
    
    return render(request, 'shops/product_detail.html', context)
