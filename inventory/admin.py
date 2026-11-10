from django.contrib import admin
from .models import StockLog

@admin.register(StockLog)
class StockLogAdmin(admin.ModelAdmin):
    list_display = ('product', 'change_type', 'quantity_changed', 'previous_stock', 'new_stock', 'reference_id', 'created_at')
    list_filter = ('change_type', 'created_at')
    search_fields = ('product__name', 'reference_id', 'remarks')
