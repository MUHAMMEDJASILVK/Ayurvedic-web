import uuid
from django.db import models
from django.conf import settings
from catalog.models import Product

class Order(models.Model):
    PAYMENT_CHOICES = (
        ('upi', 'UPI / QR Code (PhonePe, GPay, Paytm)'),
        ('card', 'Credit / Debit Card (Visa, RuPay, MasterCard)'),
        ('netbanking', 'Net Banking (SBI, HDFC, ICICI, Federal Bank)'),
        ('cod', 'Cash on Delivery (Pay at Doorstep)'),
    )

    STATUS_CHOICES = (
        ('placed', 'Order Placed'),
        ('confirmed', 'Order Confirmed'),
        ('processing', 'Processing & Packing'),
        ('shipped', 'Dispatched / Shipped'),
        ('out_for_delivery', 'Out for Delivery'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    )

    order_number = models.CharField(max_length=40, unique=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='orders')
    
    # Customer and delivery info
    full_name = models.CharField(max_length=150)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    shipping_address = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100, default='Kerala')
    pincode = models.CharField(max_length=10)
    landmark = models.CharField(max_length=150, blank=True)

    # Billing summary
    total_mrp = models.DecimalField(max_digits=10, decimal_places=2)
    total_discount = models.DecimalField(max_digits=10, decimal_places=2)
    delivery_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    grand_total = models.DecimalField(max_digits=10, decimal_places=2)

    # Payment details
    payment_method = models.CharField(max_length=30, choices=PAYMENT_CHOICES, default='upi')
    payment_status = models.CharField(max_length=20, default='completed')
    transaction_id = models.CharField(max_length=64, blank=True)

    # Fulfillment & tracking
    order_status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='placed')
    tracking_number = models.CharField(max_length=50, blank=True)
    courier_partner = models.CharField(max_length=80, default="Kerala Ayurveda Express / Speed Post")
    delivery_date_est = models.CharField(max_length=50, default="3-5 Business Days")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.order_number:
            self.order_number = f"KAS-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Order #{self.order_number} by {self.full_name} (₹{self.grand_total})"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True)
    product_name = models.CharField(max_length=200)
    brand_name = models.CharField(max_length=120)
    volume_weight = models.CharField(max_length=80, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    mrp = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)
    line_total = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantity} x {self.product_name} in {self.order.order_number}"
