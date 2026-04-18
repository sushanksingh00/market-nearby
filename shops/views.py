from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.db import transaction
from django.contrib import messages
from django.urls import reverse
from django.views.decorators.http import require_POST
from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse
from decimal import Decimal
import math
from datetime import timedelta
from django.utils import timezone
from .models import Shop, Product, Category, Order, OrderItem
from .forms import ProductForm, ShopForm
from .geo import bounding_box_km, haversine_km, parse_float

ORDER_RADIUS_KM = 10.0


def _get_user_lat_lng(request):
    lat = parse_float(request.session.get('user_lat'))
    lng = parse_float(request.session.get('user_lng'))

    # Fallback to cookies if session values are missing.
    if lat is None or lng is None:
        c_lat = parse_float(request.COOKIES.get('user_lat'))
        c_lng = parse_float(request.COOKIES.get('user_lng'))
        if c_lat is not None and c_lng is not None:
            lat, lng = c_lat, c_lng
            request.session['user_lat'] = lat
            request.session['user_lng'] = lng
    return lat, lng


def _distance_km_user_to_shop(request, shop: Shop):
    user_lat, user_lng = _get_user_lat_lng(request)
    if user_lat is None or user_lng is None:
        return None
    if shop is None or shop.latitude is None or shop.longitude is None:
        return None
    return haversine_km(user_lat, user_lng, float(shop.latitude), float(shop.longitude))


def _is_shop_orderable(request, shop: Shop, radius_km: float = ORDER_RADIUS_KM) -> bool:
    d = _distance_km_user_to_shop(request, shop)
    # If distance can't be computed (missing user/shop location), block ordering.
    if d is None:
        return False
    return d <= float(radius_km)


def _require_shop_orderable(request, shop: Shop, radius_km: float = ORDER_RADIUS_KM) -> bool:
    user_lat, user_lng = _get_user_lat_lng(request)
    if user_lat is None or user_lng is None:
        messages.error(request, 'Please set your location to order.')
        return False
    if shop is None or shop.latitude is None or shop.longitude is None:
        messages.error(request, 'This shop has no location set, so ordering is disabled.')
        return False
    d = haversine_km(user_lat, user_lng, float(shop.latitude), float(shop.longitude))
    if d > float(radius_km):
        messages.error(request, 'Ordering is blocked beyond 10 km from your location.')
        return False
    return True


def _get_cart(request):
    cart = request.session.get('cart')
    if not isinstance(cart, dict):
        cart = {}
        request.session['cart'] = cart
    return cart


def _get_cart_shop_id(request):
    shop_id = request.session.get('cart_shop_id')
    try:
        return int(shop_id) if shop_id is not None else None
    except (TypeError, ValueError):
        return None


def _set_cart_shop_id(request, shop_id: int | None):
    if shop_id is None:
        request.session.pop('cart_shop_id', None)
    else:
        request.session['cart_shop_id'] = int(shop_id)
    request.session.modified = True


def cart_detail(request):
    cart = _get_cart(request)
    cart_shop_id = _get_cart_shop_id(request)
    product_ids = [int(pid) for pid in cart.keys() if str(pid).isdigit()]

    products = Product.objects.filter(id__in=product_ids).select_related('shop', 'category')
    products_by_id = {p.id: p for p in products}

    items = []
    total = Decimal('0')
    for pid_str, qty in cart.items():
        try:
            pid = int(pid_str)
            qty_i = int(qty)
        except (TypeError, ValueError):
            continue
        if qty_i <= 0:
            continue
        product = products_by_id.get(pid)
        if product is None:
            continue

        # Enforce single-shop cart even if session was tampered.
        if cart_shop_id is not None and product.shop_id != cart_shop_id:
            continue
        line_total = (product.price or Decimal('0')) * qty_i
        total += line_total
        items.append({
            'product': product,
            'quantity': qty_i,
            'line_total': line_total,
        })

    items.sort(key=lambda x: x['product'].name.lower())

    cart_shop = None
    if cart_shop_id is not None:
        cart_shop = Shop.objects.filter(id=cart_shop_id).first()

    pickup_eta_min = 10
    delivery_distance_km = None
    delivery_distance_km_decimal = None
    delivery_eta_min = None
    delivery_fee_estimate = None
    can_pickup = bool(cart_shop and getattr(cart_shop, 'offers_pickup', False))
    can_delivery = bool(cart_shop and getattr(cart_shop, 'offers_delivery', False))

    if can_delivery:
        user_lat = parse_float(request.session.get('user_lat'))
        user_lng = parse_float(request.session.get('user_lng'))
        if user_lat is not None and user_lng is not None and cart_shop and cart_shop.latitude is not None and cart_shop.longitude is not None:
            delivery_distance_km = haversine_km(user_lat, user_lng, float(cart_shop.latitude), float(cart_shop.longitude))
            if delivery_distance_km is not None and delivery_distance_km >= 0:
                delivery_distance_km_decimal = Decimal(str(delivery_distance_km)).quantize(Decimal('0.01'))
                delivery_eta_min = int(math.ceil(10 + (5 * float(delivery_distance_km))))
                rate = (cart_shop.delivery_charge_per_km or Decimal('0.00'))
                delivery_fee_estimate = (rate * delivery_distance_km_decimal).quantize(Decimal('0.01'))

    return render(request, 'shops/cart.html', {
        'items': items,
        'total': total,
        'cart_shop': cart_shop,
        'pickup_eta_min': pickup_eta_min,
        'delivery_distance_km': delivery_distance_km,
        'delivery_distance_km_decimal': delivery_distance_km_decimal,
        'delivery_eta_min': delivery_eta_min,
        'delivery_fee_estimate': delivery_fee_estimate,
        'can_pickup': can_pickup,
        'can_delivery': can_delivery,
    })


@require_POST
@login_required
def place_order(request):
    cart = _get_cart(request)
    if not cart:
        messages.error(request, 'Your cart is empty.')
        return redirect('shops:cart_detail')

    cart_shop_id = _get_cart_shop_id(request)
    if cart_shop_id is None:
        messages.error(request, 'Please add items from a shop before placing an order.')
        return redirect('shops:cart_detail')

    shop = Shop.objects.filter(id=cart_shop_id).first()
    if shop is None:
        messages.error(request, 'Shop not found for this cart.')
        return redirect('shops:cart_detail')

    if not _require_shop_orderable(request, shop):
        return redirect('shops:cart_detail')

    method = (request.POST.get('method') or '').lower()
    if method not in {'pickup', 'delivery'}:
        messages.error(request, 'Please choose pickup or delivery.')
        return redirect('shops:cart_detail')

    if method == 'pickup':
        if not getattr(shop, 'offers_pickup', False):
            messages.error(request, 'Pickup is not available for this shop.')
            return redirect('shops:cart_detail')
        eta_min = 10

    distance_km = None
    delivery_rate = Decimal('0.00')
    delivery_fee = Decimal('0.00')

    if method == 'delivery':
        if not getattr(shop, 'offers_delivery', False):
            messages.error(request, 'Delivery is not available for this shop.')
            return redirect('shops:cart_detail')

        user_lat = parse_float(request.session.get('user_lat'))
        user_lng = parse_float(request.session.get('user_lng'))
        if user_lat is None or user_lng is None:
            messages.error(request, 'Please set your location to place a delivery order.')
            return redirect('shops:cart_detail')
        if shop.latitude is None or shop.longitude is None:
            messages.error(request, 'This shop has no location set, so delivery time cannot be calculated.')
            return redirect('shops:cart_detail')

        distance_km_f = haversine_km(user_lat, user_lng, float(shop.latitude), float(shop.longitude))
        distance_km = Decimal(str(distance_km_f)).quantize(Decimal('0.01'))
        eta_min = int(math.ceil(10 + (5 * float(distance_km_f))))

        delivery_rate = (shop.delivery_charge_per_km or Decimal('0.00'))
        delivery_fee = (delivery_rate * distance_km).quantize(Decimal('0.01'))

    # Build order items from trusted DB prices (avoid session tampering).
    product_ids = [int(pid) for pid in cart.keys() if str(pid).isdigit()]
    products = Product.objects.filter(id__in=product_ids, shop_id=shop.id).select_related('shop')
    products_by_id = {p.id: p for p in products}

    items_to_create = []
    subtotal = Decimal('0.00')
    for pid_str, qty in cart.items():
        try:
            pid = int(pid_str)
            qty_i = int(qty)
        except (TypeError, ValueError):
            continue
        if qty_i <= 0:
            continue
        product = products_by_id.get(pid)
        if product is None:
            continue
        unit_price = product.price or Decimal('0.00')
        line_total = (unit_price * qty_i).quantize(Decimal('0.01'))
        subtotal += line_total
        items_to_create.append({
            'product': product,
            'product_name': product.name,
            'unit_price': unit_price,
            'quantity': qty_i,
            'line_total': line_total,
        })

    if not items_to_create:
        messages.error(request, 'Your cart has no valid items.')
        return redirect('shops:cart_detail')

    total = (subtotal + delivery_fee).quantize(Decimal('0.01'))
    now = timezone.now()
    expected_at = now + timedelta(minutes=int(eta_min))

    # Ensure session key exists so anonymous users can still see order history.
    if not request.session.session_key:
        request.session.save()
    session_key = request.session.session_key

    with transaction.atomic():
        order = Order.objects.create(
            user=request.user if getattr(request, 'user', None) and request.user.is_authenticated else None,
            session_key=session_key,
            shop=shop,
            method=method,
            status='placed',
            distance_km=distance_km,
            delivery_charge_per_km=delivery_rate,
            delivery_fee=delivery_fee,
            subtotal=subtotal.quantize(Decimal('0.01')),
            total=total,
            eta_minutes=int(eta_min),
            expected_at=expected_at,
        )
        OrderItem.objects.bulk_create([
            OrderItem(
                order=order,
                product=i['product'],
                product_name=i['product_name'],
                unit_price=i['unit_price'],
                quantity=i['quantity'],
                line_total=i['line_total'],
            ) for i in items_to_create
        ])

    if method == 'pickup':
        messages.success(request, f'Order placed for pickup. Ready in ~{eta_min} min.')
    else:
        messages.success(request, f'Order placed for delivery. Arrives in ~{eta_min} min.')

    # Clear cart after placing order
    request.session['cart'] = {}
    _set_cart_shop_id(request, None)
    request.session.modified = True
    return redirect('shops:cart_detail')


def orders_list(request):
    session_key = request.session.session_key
    if not session_key:
        request.session.save()
        session_key = request.session.session_key

    q = Q(session_key=session_key)
    if request.user.is_authenticated:
        q = q | Q(user=request.user)

    orders = Order.objects.filter(q).select_related('shop').order_by('-created_at')
    return render(request, 'shops/orders.html', {'orders': orders})


def order_detail(request, order_id: int):
    session_key = request.session.session_key
    if not session_key:
        request.session.save()
        session_key = request.session.session_key

    q = Q(id=order_id) & Q(session_key=session_key)
    if request.user.is_authenticated:
        q = Q(id=order_id) & (Q(session_key=session_key) | Q(user=request.user))

    order = get_object_or_404(Order.objects.select_related('shop'), q)
    items = list(order.items.all())
    return render(request, 'shops/order_detail.html', {'order': order, 'items': items})


@login_required
def shop_orders(request):
    if request.user.user_type != 'shopkeeper':
        messages.error(request, 'Only shopkeepers can access shop orders.')
        return redirect('shops:index')

    shops_qs = _owned_shops(request.user)
    if not shops_qs.exists():
        return redirect('shops:shop_create')

    shop_id = request.GET.get('shop')
    if not shop_id:
        if shops_qs.count() == 1:
            shop = shops_qs.first()
            return redirect(f"{reverse('shops:shop_orders')}?shop={shop.id}")
        return render(request, 'shops/select_shop.html', {
            'shops': shops_qs.order_by('name'),
            'action': 'View Orders',
            'target_url': reverse('shops:shop_orders'),
        })

    shop = get_object_or_404(Shop, id=shop_id, owner=request.user)
    orders = (
        Order.objects.filter(shop=shop)
        .select_related('shop', 'user')
        .prefetch_related('items')
        .order_by('-created_at')
    )
    return render(request, 'shops/shop_orders.html', {
        'shop': shop,
        'orders': orders,
        'owned_shops': shops_qs.order_by('name'),
    })


@login_required
@require_POST
def shop_order_update_status(request, order_id: int):
    if request.user.user_type != 'shopkeeper':
        messages.error(request, 'Not authorized.')
        return redirect('shops:index')

    order = get_object_or_404(Order.objects.select_related('shop'), id=order_id, shop__owner=request.user)
    new_status = (request.POST.get('status') or '').strip()

    allowed = {'ready_for_pickup', 'out_for_delivery'}
    if new_status not in allowed:
        messages.error(request, 'Invalid status.')
        return redirect(f"{reverse('shops:shop_orders')}?shop={order.shop_id}")

    # Ensure status matches order method.
    if order.method == 'pickup' and new_status != 'ready_for_pickup':
        messages.error(request, 'Pickup orders can only be marked as Ready for pickup.')
        return redirect(f"{reverse('shops:shop_orders')}?shop={order.shop_id}")
    if order.method == 'delivery' and new_status != 'out_for_delivery':
        messages.error(request, 'Delivery orders can only be marked as Out for delivery.')
        return redirect(f"{reverse('shops:shop_orders')}?shop={order.shop_id}")

    order.status = new_status
    order.save(update_fields=['status', 'updated_at'])
    messages.success(request, 'Order status updated.')
    return redirect(f"{reverse('shops:shop_orders')}?shop={order.shop_id}")


@login_required
def shop_order_detail(request, order_id: int):
    if request.user.user_type != 'shopkeeper':
        messages.error(request, 'Not authorized.')
        return redirect('shops:index')

    order = get_object_or_404(
        Order.objects.select_related('shop', 'user').prefetch_related('items'),
        id=order_id,
        shop__owner=request.user,
    )
    items = list(order.items.all())
    return render(request, 'shops/shop_order_detail.html', {'order': order, 'items': items, 'shop': order.shop})


@require_POST
def cart_add(request, product_id: int):
    product = get_object_or_404(Product, id=product_id)
    if not product.in_stock:
        messages.error(request, 'This product is currently out of stock.')
        return redirect('shops:product_detail', pk=product.id)

    qty_raw = request.POST.get('quantity', '1')
    try:
        qty = int(qty_raw)
    except (TypeError, ValueError):
        qty = 1
    if qty <= 0:
        qty = 1

    if not _require_shop_orderable(request, product.shop):
        next_url = request.POST.get('next')
        if next_url:
            parsed = urlparse(next_url)
            if not parsed.scheme and not parsed.netloc:
                return redirect(next_url)
        return redirect('shops:product_detail', pk=product.id)

    cart = _get_cart(request)
    existing_shop_id = _get_cart_shop_id(request)
    if existing_shop_id is None:
        _set_cart_shop_id(request, product.shop_id)
    elif existing_shop_id != product.shop_id:
        prev_shop_name = Shop.objects.filter(id=existing_shop_id).values_list('name', flat=True).first() or 'previous shop'
        new_shop_name = product.shop.name
        # Latest shop wins: replace cart contents.
        request.session['cart'] = {}
        cart = request.session['cart']
        _set_cart_shop_id(request, product.shop_id)
        messages.warning(request, f"Cart cleared: switched from {prev_shop_name} to {new_shop_name}.")

    key = str(product.id)
    current = int(cart.get(key, 0) or 0)
    cart[key] = current + qty
    request.session.modified = True

    next_url = request.POST.get('next')
    if next_url:
        parsed = urlparse(next_url)
        if not parsed.scheme and not parsed.netloc:
            return redirect(next_url)
    return redirect('shops:cart_detail')


@require_POST
def cart_update(request, product_id: int):
    cart = _get_cart(request)
    key = str(product_id)
    if key not in cart:
        return redirect('shops:cart_detail')

    action = (request.POST.get('action') or '').lower()
    try:
        current_qty = int(cart.get(key, 0) or 0)
    except (TypeError, ValueError):
        current_qty = 0

    new_qty = current_qty
    if action == 'inc':
        new_qty = current_qty + 1
    elif action == 'dec':
        new_qty = current_qty - 1
    elif action == 'set':
        try:
            new_qty = int(request.POST.get('quantity', current_qty))
        except (TypeError, ValueError):
            new_qty = current_qty

    if new_qty <= 0:
        cart.pop(key, None)
    else:
        cart[key] = new_qty
    request.session.modified = True

    if not cart:
        _set_cart_shop_id(request, None)

    next_url = request.POST.get('next')
    if next_url:
        parsed = urlparse(next_url)
        if not parsed.scheme and not parsed.netloc:
            return redirect(next_url)
    return redirect('shops:cart_detail')


@require_POST
def cart_remove(request, product_id: int):
    cart = _get_cart(request)
    cart.pop(str(product_id), None)
    request.session.modified = True

    if not cart:
        _set_cart_shop_id(request, None)

    next_url = request.POST.get('next')
    if next_url:
        parsed = urlparse(next_url)
        if not parsed.scheme and not parsed.netloc:
            return redirect(next_url)
    return redirect('shops:cart_detail')


@require_POST
def cart_clear(request):
    request.session['cart'] = {}
    _set_cart_shop_id(request, None)
    request.session.modified = True
    return redirect('shops:cart_detail')


@require_POST
def set_location(request):
    """Store user's location in session without putting it in the URL."""
    lat = parse_float(request.POST.get('lat'))
    lng = parse_float(request.POST.get('lng'))
    if lat is not None and lng is not None:
        request.session['user_lat'] = lat
        request.session['user_lng'] = lng
    else:
        messages.error(request, 'Invalid location coordinates.')

    next_url = request.POST.get('next') or reverse('shops:shop_list')
    # Only allow relative redirects and strip lat/lng from query params.
    parsed = urlparse(next_url)
    if parsed.scheme or parsed.netloc:
        response = redirect('shops:shop_list')
        if lat is not None and lng is not None:
            response.set_cookie('user_lat', str(lat), max_age=60 * 60 * 24 * 30, samesite='Lax')
            response.set_cookie('user_lng', str(lng), max_age=60 * 60 * 24 * 30, samesite='Lax')
        return response

    kept = [(k, v) for (k, v) in parse_qsl(parsed.query, keep_blank_values=True) if k not in {'lat', 'lng'}]
    clean_query = urlencode(kept)
    clean = urlunparse(("", "", parsed.path or reverse('shops:shop_list'), parsed.params, clean_query, parsed.fragment))
    response = redirect(clean)
    if lat is not None and lng is not None:
        response.set_cookie('user_lat', str(lat), max_age=60 * 60 * 24 * 30, samesite='Lax')
        response.set_cookie('user_lng', str(lng), max_age=60 * 60 * 24 * 30, samesite='Lax')
    return response

def index(request):
    """Main page showing shops and products"""
    # Get featured shops
    shops = list(Shop.objects.select_related('owner').prefetch_related('categories__category').all()[:6])
    
    # Get featured products
    products = Product.objects.select_related('shop', 'category').all()[:8]
    
    # Get categories
    categories = Category.objects.all()
    
    # Get search query
    search_query = request.GET.get('search', '')
    location = request.GET.get('location', '')

    # If user location is known (saved from shop list), show real distance on cards.
    user_lat = parse_float(request.session.get('user_lat'))
    user_lng = parse_float(request.session.get('user_lng'))
    if user_lat is not None and user_lng is not None:
        for shop in shops:
            if shop.latitude is None or shop.longitude is None:
                continue
            shop.distance_km = haversine_km(user_lat, user_lng, float(shop.latitude), float(shop.longitude))
    
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
    matching_products = Product.objects.none()
    
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

    # Location-based filtering (within 10km, nearest -> farthest)
    lat = parse_float(request.GET.get('lat'))
    lng = parse_float(request.GET.get('lng'))
    if lat is None or lng is None:
        # Fallback to last known location
        lat = parse_float(request.session.get('user_lat'))
        lng = parse_float(request.session.get('user_lng'))
    else:
        # Persist for future pages
        request.session['user_lat'] = lat
        request.session['user_lng'] = lng

    radius_km = 10.0
    shops_list = None
    if lat is not None and lng is not None:
        bbox = bounding_box_km(lat, lng, radius_km)

        # Fast bounding-box prefilter in SQL
        shops = shops.filter(
            latitude__isnull=False,
            longitude__isnull=False,
            latitude__gte=Decimal(str(bbox.min_lat)),
            latitude__lte=Decimal(str(bbox.max_lat)),
            longitude__gte=Decimal(str(bbox.min_lng)),
            longitude__lte=Decimal(str(bbox.max_lng)),
        )

        shops_list = []
        for shop in shops:
            d_km = haversine_km(lat, lng, float(shop.latitude), float(shop.longitude))
            if d_km <= radius_km:
                shop.distance_km = d_km
                shops_list.append(shop)
        shops_list.sort(key=lambda s: getattr(s, 'distance_km', float('inf')))
    else:
        messages.info(request, 'Share your location to see shops within 10 km.')

    if search_query:
        matching_products = Product.objects.select_related('shop', 'category').filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(shop__name__icontains=search_query) |
            Q(category__name__icontains=search_query)
        )

        if category_id:
            matching_products = matching_products.filter(category_id=category_id)

        # Keep product matches aligned with currently visible shop scope.
        if shops_list is not None:
            visible_shop_ids = [shop.id for shop in shops_list]
            matching_products = matching_products.filter(shop_id__in=visible_shop_ids)

        matching_products = matching_products.order_by('-created_at')[:12]
    
    # Pagination
    paginator = Paginator(shops_list if shops_list is not None else shops, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    categories = Category.objects.all()
    
    context = {
        'page_obj': page_obj,
        'categories': categories,
        'matching_products': matching_products,
        'search_query': search_query,
        'selected_category': category_id,
        'location': location,
        'user_lat': lat,
        'user_lng': lng,
        'radius_km': radius_km,
    }
    
    return render(request, 'shops/shop_list.html', context)

def shop_detail(request, pk):
    """Detailed view of a shop"""
    shop = get_object_or_404(Shop, pk=pk)
    products = Product.objects.filter(shop=shop).select_related('category')
    reviews = shop.reviews.select_related('user').all()[:10]

    distance_km = _distance_km_user_to_shop(request, shop)
    can_order = _is_shop_orderable(request, shop)
    order_block_reason = None
    if not can_order:
        user_lat, user_lng = _get_user_lat_lng(request)
        if user_lat is None or user_lng is None:
            order_block_reason = 'Set your location to order.'
        else:
            order_block_reason = 'Out of range (> 10 km).'
    
    context = {
        'shop': shop,
        'products': products,
        'reviews': reviews,
        'can_order': can_order,
        'order_block_reason': order_block_reason,
        'distance_km': distance_km,
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

    user_lat, user_lng = _get_user_lat_lng(request)
    shop_orderable: dict[int, bool] = {}
    shop_reason: dict[int, str | None] = {}
    if user_lat is None or user_lng is None:
        for product in page_obj:
            setattr(product, 'can_order', False)
            setattr(product, 'order_block_reason', 'Set your location to order.')
    else:
        for product in page_obj:
            sid = getattr(product, 'shop_id', None)
            if not isinstance(sid, int):
                setattr(product, 'can_order', False)
                setattr(product, 'order_block_reason', 'Set your location to order.')
                continue
            if sid not in shop_orderable:
                shop = getattr(product, 'shop', None)
                if shop is None or shop.latitude is None or shop.longitude is None:
                    shop_orderable[sid] = False
                    shop_reason[sid] = 'Ordering disabled (shop missing location).'
                else:
                    d = haversine_km(user_lat, user_lng, float(shop.latitude), float(shop.longitude))
                    ok = d <= ORDER_RADIUS_KM
                    shop_orderable[sid] = ok
                    shop_reason[sid] = None if ok else 'Out of range (> 10 km).'
            setattr(product, 'can_order', shop_orderable[sid])
            setattr(product, 'order_block_reason', shop_reason.get(sid))
    
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
        'can_order': _is_shop_orderable(request, product.shop),
    }

    if not context['can_order']:
        user_lat, user_lng = _get_user_lat_lng(request)
        if user_lat is None or user_lng is None:
            context['order_block_reason'] = 'Set your location to order.'
        else:
            context['order_block_reason'] = 'Out of range (> 10 km).'
    
    return render(request, 'shops/product_detail.html', context)

def _get_owned_shop_or_403(user):
    try:
        return Shop.objects.get(owner=user)
    except Shop.DoesNotExist:
        return None

def _owned_shops(user):
    return Shop.objects.filter(owner=user)


@login_required
def shop_create(request):
    if request.user.user_type != 'shopkeeper':
        messages.error(request, 'Only shopkeepers can create shops.')
        return redirect('shops:index')

    if request.method == 'POST':
        form = ShopForm(request.POST)
        if form.is_valid():
            shop = form.save(commit=False)
            shop.owner = request.user
            shop.save()
            messages.success(request, 'Shop created successfully.')
            return redirect(f"{reverse('shops:dashboard')}?shop={shop.id}")
    else:
        # Pre-fill from last known user location if any
        initial = {}
        lat = parse_float(request.session.get('user_lat'))
        lng = parse_float(request.session.get('user_lng'))
        if lat is not None and lng is not None:
            initial = {'latitude': lat, 'longitude': lng}
        form = ShopForm(initial=initial)
    return render(request, 'shops/shop_create.html', {'form': form})

@login_required
def dashboard(request):
    if request.user.user_type != 'shopkeeper':
        messages.error(request, 'Only shopkeepers can access the dashboard.')
        return redirect('shops:index')
    shops_qs = _owned_shops(request.user)
    if not shops_qs.exists():
        return redirect('shops:shop_create')

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
        form = ProductForm(request.POST, shop=shop)
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
        form = ProductForm(request.POST, instance=product, shop=shop)
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
