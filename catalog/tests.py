from django.test import TestCase, Client
from django.urls import reverse
from catalog.models import Category, Brand, Product

class CatalogTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.cat1 = Category.objects.create(name="Ayurvedic Oils", slug="ayurvedic-oils")
        self.cat2 = Category.objects.create(name="Medicines & Tablets", slug="medicines-tablets")
        
        self.brand1 = Brand.objects.create(name="Kottakkal Arya Vaidya Sala", slug="kottakkal-arya-vaidya-sala", logo_badge="AVS")
        self.brand2 = Brand.objects.create(name="Kerala Ayurveda", slug="kerala-ayurveda", logo_badge="KAL")

        self.p1 = Product.objects.create(
            name="Dhanwantharam Thailam",
            category=self.cat1,
            brand=self.brand1,
            sku="KAS-001-AVS",
            price=280,
            mrp=320,
            stock=45,
            volume_weight="200 ml",
            rating=4.8,
            rating_count=320
        )
        self.p2 = Product.objects.create(
            name="Triphala Tablets",
            category=self.cat2,
            brand=self.brand2,
            sku="KAS-021-KAL",
            price=180,
            mrp=210,
            stock=15,
            volume_weight="60 Tablets",
            rating=4.5,
            rating_count=180
        )

    def test_filter_by_category(self):
        res = self.client.get(reverse('home') + '?category=ayurvedic-oils')
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, "Dhanwantharam Thailam")
        self.assertNotContains(res, "Triphala Tablets")

    def test_filter_by_brand(self):
        res = self.client.get(reverse('home') + '?brand=kerala-ayurveda')
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, "Triphala Tablets")
        self.assertNotContains(res, "Dhanwantharam Thailam")

    def test_search_query(self):
        res = self.client.get(reverse('home') + '?q=Dhanwantharam')
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, "Dhanwantharam Thailam")
        self.assertNotContains(res, "Triphala Tablets")

    def test_product_detail_page(self):
        res = self.client.get(reverse('product_detail', args=[self.p1.slug]))
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, "Dhanwantharam Thailam")
        self.assertContains(res, "Kottakkal Arya Vaidya Sala")
        self.assertContains(res, "In Stock")

    def test_search_suggestions_api(self):
        res = self.client.get(reverse('search_suggest') + '?q=Triph')
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertTrue(len(data['results']) > 0)
        self.assertEqual(data['results'][0]['title'], 'Triphala Tablets')
