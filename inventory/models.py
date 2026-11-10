from django.db import models
from django.conf import settings
from catalog.models import Product

class StockLog(models.Model):
    CHANGE_TYPES = (
        ('restock', 'Restock / Inward Shipment'),
        ('order_deduct', 'Customer Order Deduction'),
        ('adjustment', 'Manual Inventory Adjustment'),
        ('damaged', 'Damaged / Expired Removal'),
        ('return', 'Customer Return'),
    )

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='stock_logs')
    change_type = models.CharField(max_length=20, choices=CHANGE_TYPES)
    quantity_changed = models.IntegerField(help_text="Positive for addition, negative for deduction")
    previous_stock = models.IntegerField()
    new_stock = models.IntegerField()
    reference_id = models.CharField(max_length=100, blank=True, help_text="Order ID or Invoice Number")
    remarks = models.CharField(max_length=255, blank=True)
    performed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.product.name}: {self.quantity_changed:+d} units ({self.change_type})"
