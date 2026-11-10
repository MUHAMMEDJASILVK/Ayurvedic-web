from django.test import TestCase, Client
from django.urls import reverse
from accounts.models import User
from catalog.models import Category, Brand, Product
from inventory.models import StockLog
from orders.models import Order

class InventoryTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin = User.objects.create_user(
            username='admin_test',
            email='admin@test.com',
            phone_number='9876543210',
            password='password123',
            role='admin',
            is_staff=True,
            is_active=True,
            is_verified=True
        )
        self.cat = Category.objects.create(name="Ayurvedic Oils", slug="ayurvedic-oils")
        self.brand = Brand.objects.create(name="Kottakkal Arya Vaidya Sala", slug="kottakkal-avs", logo_badge="AVS")
        self.product = Product.objects.create(
            name="Ksheerabala Thailam",
            category=self.cat,
            brand=self.brand,
            sku="KAS-002-AVS",
            price=310,
            mrp=360,
            stock=8, # low stock
            volume_weight="200 ml"
        )

    def test_seller_dashboard_access(self):
        self.client.login(email='admin@test.com', password='password123')
        res = self.client.get(reverse('inventory_dashboard'))
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, "Seller Central")
        self.assertContains(res, "Ksheerabala Thailam")

    def test_update_stock_restock(self):
        self.client.login(email='admin@test.com', password='password123')
        res = self.client.post(reverse('update_stock', args=[self.product.id]), {
            'action_type': 'add',
            'quantity': 25,
            'remarks': 'Test Restock Shipment'
        })
        self.assertEqual(res.status_code, 302)
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 33) # 8 + 25 = 33

        # Check stock log
        log = StockLog.objects.filter(product=self.product).first()
        self.assertIsNotNone(log)
        self.assertEqual(log.quantity_changed, 25)
        self.assertEqual(log.previous_stock, 8)
        self.assertEqual(log.new_stock, 33)
