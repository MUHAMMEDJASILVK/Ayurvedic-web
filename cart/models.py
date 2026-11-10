from django.db import models
from django.conf import settings
from catalog.models import Product

class Cart(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True, related_name='carts')
    session_key = models.CharField(max_length=40, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Cart #{self.id} ({self.user or self.session_key})"

    @property
    def total_items(self):
        return sum(item.quantity for item in self.items.all())

    @property
    def subtotal_mrp(self):
        return sum(item.product.mrp * item.quantity for item in self.items.all())

    @property
    def subtotal_price(self):
        return sum(item.product.price * item.quantity for item in self.items.all())

    @property
    def total_discount(self):
        return max(0, self.subtotal_mrp - self.subtotal_price)

    @property
    def delivery_fee(self):
        # Free delivery over ₹499 like Amazon/Flipkart
        if self.subtotal_price >= 499 or self.total_items == 0:
            return 0
        return 40

    @property
    def grand_total(self):
        return self.subtotal_price + self.delivery_fee


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('cart', 'product')

    def __str__(self):
        return f"{self.quantity}x {self.product.name}"

    @property
    def line_total(self):
        return self.product.price * self.quantity

    @property
    def line_mrp_total(self):
        return self.product.mrp * self.quantity

    @property
    def line_savings(self):
        return (self.product.mrp - self.product.price) * self.quantity
