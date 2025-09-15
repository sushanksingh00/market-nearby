from django.urls import path
from . import views

app_name = 'shops'

urlpatterns = [
    path('', views.index, name='index'),
    path('shops/', views.shop_list, name='shop_list'),
    path('shops/<int:pk>/', views.shop_detail, name='shop_detail'),
    path('products/', views.product_list, name='product_list'),
    path('products/<int:pk>/', views.product_detail, name='product_detail'),
]
