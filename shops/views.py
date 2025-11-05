from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib import messages
from django.urls import reverse
from .models import Shop, Product, Category
from .forms import ProductForm

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

def _get_owned_shop_or_403(user):
    try:
        return Shop.objects.get(owner=user)
    except Shop.DoesNotExist:
        return None

def _owned_shops(user):
    return Shop.objects.filter(owner=user)

@login_required
def dashboard(request):
    if request.user.user_type != 'shopkeeper':
        messages.error(request, 'Only shopkeepers can access the dashboard.')
        return redirect('shops:index')
    shops_qs = _owned_shops(request.user)
    if not shops_qs.exists():
        messages.error(request, 'No shop is linked to your account. Contact admin.')
        return redirect('shops:index')

    shop_id = request.GET.get('shop')
    if not shop_id:
        if shops_qs.count() == 1:
            # Single shop, auto-select
            shop = shops_qs.first()
            return redirect(f"{reverse('shops:dashboard')}?shop={shop.id}")
        # Multiple shops: ask user to pick
        return render(request, 'shops/select_shop.html', {
            'shops': shops_qs.order_by('name'),
            'action': 'Manage Products',
            'target_url': reverse('shops:dashboard'),
        })

    shop = get_object_or_404(Shop, id=shop_id, owner=request.user)
    products = Product.objects.filter(shop=shop).select_related('category')
    return render(request, 'shops/dashboard.html', {
        'shop': shop,
        'products': products,
        'owned_shops': shops_qs.order_by('name'),
    })

@login_required
def product_create(request):
    if request.user.user_type != 'shopkeeper':
        messages.error(request, 'Not authorized.')
        return redirect('shops:index')

    shops_qs = _owned_shops(request.user)
    if not shops_qs.exists():
        messages.error(request, 'No shop is linked to your account.')
        return redirect('shops:index')

    shop_id = request.GET.get('shop') or request.POST.get('shop')
    if not shop_id:
        if shops_qs.count() == 1:
            shop = shops_qs.first()
            return redirect(f"{reverse('shops:product_create')}?shop={shop.id}")
        return render(request, 'shops/select_shop.html', {
            'shops': shops_qs.order_by('name'),
            'action': 'Add Product',
            'target_url': reverse('shops:product_create'),
        })

    shop = get_object_or_404(Shop, id=shop_id, owner=request.user)

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, shop=shop)
        if form.is_valid():
            form.save()
            messages.success(request, 'Product added successfully.')
            return redirect(f"{reverse('shops:dashboard')}?shop={shop.id}")
    else:
        form = ProductForm(shop=shop)
    return render(request, 'shops/product_form.html', {'form': form, 'shop': shop, 'mode': 'create'})

@login_required
def product_update(request, pk):
    if request.user.user_type != 'shopkeeper':
        messages.error(request, 'Not authorized.')
        return redirect('shops:index')
    product = get_object_or_404(Product, pk=pk, shop__owner=request.user)
    shop = product.shop
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product, shop=shop)
        if form.is_valid():
            form.save()
            messages.success(request, 'Product updated successfully.')
            return redirect(f"{reverse('shops:dashboard')}?shop={shop.id}")
    else:
        form = ProductForm(instance=product, shop=shop)
    return render(request, 'shops/product_form.html', {'form': form, 'shop': shop, 'mode': 'update', 'product': product})

@login_required
def product_delete(request, pk):
    if request.user.user_type != 'shopkeeper':
        messages.error(request, 'Not authorized.')
        return redirect('shops:index')
    product = get_object_or_404(Product, pk=pk, shop__owner=request.user)
    shop = product.shop
    if request.method == 'POST':
        product.delete()
        messages.success(request, 'Product deleted successfully.')
        return redirect(f"{reverse('shops:dashboard')}?shop={shop.id}")
    return render(request, 'shops/product_confirm_delete.html', {'product': product, 'shop': shop})
