from django import forms
from .models import Product, Category, ShopCategory

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            'name', 'category', 'price', 'original_price',
            'description', 'in_stock', 'stock_quantity', 'image'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        # Expect a 'shop' kwarg to filter categories and set shop on save
        self.shop = kwargs.pop('shop', None)
        super().__init__(*args, **kwargs)
        if self.shop is not None:
            allowed_category_ids = ShopCategory.objects.filter(shop=self.shop).values_list('category_id', flat=True)
            self.fields['category'].queryset = Category.objects.filter(id__in=allowed_category_ids)

    def save(self, commit=True):
        obj = super().save(commit=False)
        if self.shop is not None:
            obj.shop = self.shop
        if commit:
            obj.save()
        return obj
