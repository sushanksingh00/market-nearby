from django.urls import path
from . import views

app_name = 'shops'

urlpatterns = [
    path('', views.index, name='index'),
    path('shops/', views.shop_list, name='shop_list'),
    path('shops/<int:pk>/', views.shop_detail, name='shop_detail'),
    path('products/', views.product_list, name='product_list'),
    path('products/<int:pk>/', views.product_detail, name='product_detail'),

    # Shopkeeper dashboard + CRUD
    path('dashboard/', views.dashboard, name='dashboard'),
    path('dashboard/products/create/', views.product_create, name='product_create'),
    path('dashboard/products/<int:pk>/edit/', views.product_update, name='product_update'),
    path('dashboard/products/<int:pk>/delete/', views.product_delete, name='product_delete'),
]
