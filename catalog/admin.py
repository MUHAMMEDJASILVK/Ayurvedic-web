from django.contrib import admin
from .models import Category, Brand, Product

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'display_order')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)

@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ('name', 'logo_badge', 'established_year', 'headquarters')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name', 'headquarters')

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'brand', 'category', 'price', 'mrp', 'stock', 'volume_weight', 'is_bestseller', 'is_in_stock')
    list_filter = ('category', 'brand', 'product_type', 'is_bestseller', 'is_featured')
    search_fields = ('name', 'sku', 'brand__name', 'ingredients', 'classical_reference')
    prepopulated_fields = {'slug': ('name',)}
