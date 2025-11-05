from django.contrib import admin
from .models import Shop, Category, ShopCategory, Product, Review

# admin.site.site_header = "Vstash Admin"
admin.site.site_title = "Vstash Admin Portal"
admin.site.index_title = "Welcome to Vstash Administration"

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)

class ShopCategoryInline(admin.TabularInline):
    model = ShopCategory
    extra = 1

@admin.register(Shop)
class ShopAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'address', 'phone', 'is_open', 'rating', 'created_at')
    list_filter = ('is_open', 'created_at', 'rating')
    search_fields = ('name', 'owner__username', 'address')
    inlines = [ShopCategoryInline]
    readonly_fields = ('created_at', 'updated_at')

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'shop', 'category', 'price', 'in_stock', 'stock_quantity', 'rating')
    list_filter = ('in_stock', 'category', 'created_at')
    search_fields = ('name', 'shop__name', 'category__name')
    readonly_fields = ('created_at', 'updated_at')

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('user', 'get_target', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('user__username', 'shop__name', 'product__name')
    readonly_fields = ('created_at',)
    
    def get_target(self, obj):
        return obj.shop.name if obj.shop else obj.product.name
    get_target.short_description = 'Target'
