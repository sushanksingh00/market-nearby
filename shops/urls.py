from django.urls import path
from . import views

app_name = 'shops'

urlpatterns = [
    path('', views.index, name='index'),
    path('shops/', views.shop_list, name='shop_list'),
    path('shops/set-location/', views.set_location, name='set_location'),
    path('shops/<int:pk>/', views.shop_detail, name='shop_detail'),
    path('products/', views.product_list, name='product_list'),
    path('products/<int:pk>/', views.product_detail, name='product_detail'),

    # Cart
    path('cart/', views.cart_detail, name='cart_detail'),
    path('cart/add/<int:product_id>/', views.cart_add, name='cart_add'),
    path('cart/update/<int:product_id>/', views.cart_update, name='cart_update'),
    path('cart/remove/<int:product_id>/', views.cart_remove, name='cart_remove'),
    path('cart/clear/', views.cart_clear, name='cart_clear'),
    path('cart/place-order/', views.place_order, name='place_order'),

    # Orders (history)
    path('orders/', views.orders_list, name='orders_list'),
    path('orders/<int:order_id>/', views.order_detail, name='order_detail'),

    # Shopkeeper orders
    path('dashboard/orders/', views.shop_orders, name='shop_orders'),
    path('dashboard/orders/<int:order_id>/status/', views.shop_order_update_status, name='shop_order_update_status'),
    path('dashboard/orders/<int:order_id>/', views.shop_order_detail, name='shop_order_detail'),

    # Shopkeeper dashboard + CRUD
    path('dashboard/', views.dashboard, name='dashboard'),
    path('dashboard/shop/create/', views.shop_create, name='shop_create'),
    path('dashboard/products/create/', views.product_create, name='product_create'),
    path('dashboard/products/<int:pk>/edit/', views.product_update, name='product_update'),
    path('dashboard/products/<int:pk>/delete/', views.product_delete, name='product_delete'),
]
