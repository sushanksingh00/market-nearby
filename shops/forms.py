from django import forms
from .models import Product, Category, ShopCategory, Shop


class ShopForm(forms.ModelForm):
    class Meta:
        model = Shop
        fields = [
            'name',
            'address',
            'phone',
            'latitude',
            'longitude',
            'image',
            'is_open',
            'opening_time',
            'closing_time',
            'offers_delivery',
            'offers_pickup',
            'delivery_charge_per_km',
        ]
        widgets = {
            'address': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'latitude': forms.NumberInput(attrs={'class': 'form-control', 'step': 'any'}),
            'longitude': forms.NumberInput(attrs={'class': 'form-control', 'step': 'any'}),
            'is_open': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'opening_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'closing_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'offers_delivery': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'offers_pickup': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'delivery_charge_per_km': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Require location for onboarding
        self.fields['latitude'].required = True
        self.fields['longitude'].required = True

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
