from django.contrib import admin

from .models import Category, Product, Color, Size, ProductVariant  # Добавим Review позже


@admin.register(Color)
class ColorAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Size)
class SizeAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}


class ProductVariantInline(admin.TabularInline):  # Позволяет добавлять варианты прямо на странице продукта
    model = ProductVariant
    extra = 1


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'price', 'available', 'created', 'updated']
    list_filter = ['available', 'created', 'updated']
    list_editable = ['price', 'available']
    prepopulated_fields = {'slug': ('name',)}
    raw_id_fields = ['category']
    search_fields = ['name', 'description']
    inlines = [ProductVariantInline]  # Добавляем инлайн для вариантов


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}
