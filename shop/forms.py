from django import forms

from .models import Product, ProductVariant


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['category', 'name', 'slug', 'image', 'description', 'price', 'available']
        # Уберем stock отсюда, если он управляется вариантами

    # Можно добавить валидацию, если нужно


class ProductVariantForm(forms.ModelForm):
    class Meta:
        model = ProductVariant
        fields = ['color', 'size', 'price', 'stock', 'available']


# Formset для управления вариантами на форме продукта
from django.forms import inlineformset_factory

ProductVariantFormSet = inlineformset_factory(
    Product,  # Родительская модель
    ProductVariant,  # Дочерняя модель
    form=ProductVariantForm,
    extra=1,  # Количество пустых форм для новых вариантов
    can_delete=True  # Разрешить удаление вариантов
)
