from django.test import TestCase, Client
from django.urls import reverse
from accounts.models import User, OTPVerification
from catalog.models import Product, Category, Brand
from cart.models import Cart, CartItem
from orders.models import Order

class AyurvedicPortalWorkflowTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.category = Category.objects.create(name="Ayurvedic Oils", slug="ayurvedic-oils")
        self.brand = Brand.objects.create(name="Kottakkal Arya Vaidya Sala", slug="kottakkal-arya-vaidya-sala", logo_badge="AVS")
        self.product = Product.objects.create(
            name="Dhanwantharam Thailam",
            category=self.category,
            brand=self.brand,
            sku="KAS-001-AVS",
            price=280,
            mrp=320,
            stock=50,
            volume_weight="200 ml",
            short_description="Classical neuromuscular tonic",
            description="Deep muscle nourishment",
            key_benefits="Relieves joint stiffness",
            ingredients="Bala, Dasamoola, Sesame oil",
            usage_dosage="Apply warm oil",
            classical_reference="Ashtanga Hridaya"
        )

    def test_catalog_home_page(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Dhanwantharam Thailam")
        self.assertContains(response, "Kottakkal Arya Vaidya Sala")

    def test_registration_and_otp_dispatch(self):
        # 1. Register a new customer
        response = self.client.post(reverse('register'), {
            'full_name': 'Ramesh Nair',
            'email': 'ramesh.nair@example.com',
            'phone_number': '9847012345',
            'password': 'SecurePassword123',
            'confirm_password': 'SecurePassword123'
        })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('verify_otp'))

        # User is created but NOT yet verified or active
        user = User.objects.get(email='ramesh.nair@example.com')
        self.assertFalse(user.is_verified)
        self.assertFalse(user.is_active)

        # OTPVerification object exists with 6-digit codes
        otp_rec = OTPVerification.objects.filter(user=user, is_used=False).first()
        self.assertIsNotNone(otp_rec)
        self.assertEqual(len(otp_rec.email_otp), 6)
        self.assertEqual(len(otp_rec.phone_otp), 6)

        # 2. Test verify_otp GET page does NOT contain raw OTP codes in page content
        verify_page = self.client.get(reverse('verify_otp'))
        self.assertEqual(verify_page.status_code, 200)
        self.assertNotContains(verify_page, otp_rec.email_otp)
        self.assertNotContains(verify_page, otp_rec.phone_otp)
        # It displays masked email and phone
        from accounts.views import mask_email, mask_phone
        self.assertContains(verify_page, mask_email("ramesh.nair@example.com"))
        self.assertContains(verify_page, mask_phone("9847012345"))

        # 3. Test wrong OTP submission fails
        fail_response = self.client.post(reverse('verify_otp'), {
            'email_otp': '000000',
            'phone_otp': '111111'
        })
        self.assertEqual(fail_response.status_code, 200)
        user.refresh_from_db()
        self.assertFalse(user.is_verified)

        # 4. Test valid OTP submission activates user and logs in!
        success_response = self.client.post(reverse('verify_otp'), {
            'email_otp': otp_rec.email_otp,
            'phone_otp': otp_rec.phone_otp
        })
        self.assertEqual(success_response.status_code, 302)
        user.refresh_from_db()
        self.assertTrue(user.is_verified)
        self.assertTrue(user.is_active)

    def test_cart_and_checkout_inventory_deduction(self):
        # Create and log in verified user
        user = User.objects.create_user(
            username='user1',
            email='user1@example.com',
            phone_number='9876500001',
            password='password123',
            is_active=True,
            is_verified=True
        )
        self.client.login(email='user1@example.com', password='password123')

        # Add 3 units to cart
        add_res = self.client.post(reverse('add_to_cart', args=[self.product.id]), {'quantity': 3})
        self.assertEqual(add_res.status_code, 302)

        cart = Cart.objects.get(user=user)
        self.assertEqual(cart.total_items, 3)
        self.assertEqual(cart.subtotal_price, 280 * 3)

        initial_stock = self.product.stock

        # Place order
        order_res = self.client.post(reverse('place_order'), {
            'full_name': 'Test Customer',
            'email': 'user1@example.com',
            'phone': '9876500001',
            'address': 'MG Road, Marine Drive',
            'city': 'Kochi',
            'state': 'Kerala',
            'pincode': '682001',
            'payment_method': 'upi'
        })
        self.assertEqual(order_res.status_code, 302)

        # Stock should be deducted from 50 to 47!
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, initial_stock - 3)

        # Order created
        order = Order.objects.filter(user=user).first()
        self.assertIsNotNone(order)
        self.assertEqual(order.items.count(), 1)
        self.assertEqual(order.items.first().quantity, 3)
