from django.db import models
from django.utils.text import slugify

class Category(models.Model):
    name = models.CharField(max_length=120, unique=True)
    slug = models.SlugField(max_length=150, unique=True, blank=True)
    description = models.TextField(blank=True)
    icon_name = models.CharField(max_length=50, default='fa-leaf')
    display_order = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['display_order', 'name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Brand(models.Model):
    name = models.CharField(max_length=120, unique=True)
    slug = models.SlugField(max_length=150, unique=True, blank=True)
    description = models.TextField(blank=True)
    headquarters = models.CharField(max_length=150, default="Kerala, India")
    established_year = models.PositiveIntegerField(null=True, blank=True)
    logo_badge = models.CharField(max_length=50, blank=True)

    class Meta:
        ordering = ['name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Product(models.Model):
    PRODUCT_TYPE_CHOICES = (
        ('oil', 'Herbal Oil / Thailam / Keram'),
        ('tablet', 'Tablets / Gulika / Vati / Kwath Tablets'),
        ('beauty', 'Herbal Beauty / Face Pack / Gel / Soap'),
        ('arishtam', 'Arishtam / Asavam / Fermented Tonic'),
        ('choornam', 'Choornam / Herbal Powder / Kwath Churna'),
        ('lehyam', 'Lehyam / Rasayanam / Ghritham / Health Tonic'),
    )

    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=250, unique=True, blank=True)
    sku = models.CharField(max_length=50, unique=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE, related_name='products')
    product_type = models.CharField(max_length=20, choices=PRODUCT_TYPE_CHOICES, default='oil')
    
    # Pricing & Stock
    price = models.DecimalField(max_digits=10, decimal_places=2, help_text="Current Selling Price in INR")
    mrp = models.DecimalField(max_digits=10, decimal_places=2, help_text="Maximum Retail Price in INR")
    discount_percent = models.PositiveIntegerField(default=0)
    stock = models.IntegerField(default=45, help_text="Current Inventory Count")
    low_stock_threshold = models.IntegerField(default=12)
    volume_weight = models.CharField(max_length=80, help_text="e.g. 200 ml, 450 ml, 60 Tablets, 100 g")
    
    # Details & Ayurveda specifications
    short_description = models.CharField(max_length=300)
    description = models.TextField()
    key_benefits = models.TextField(help_text="Key therapeutic benefits")
    ingredients = models.TextField(help_text="Key classical herbs and ingredients")
    usage_dosage = models.TextField(help_text="Directions for use / dosage")
    classical_reference = models.CharField(max_length=150, default="Sahasrayogam / Ashtanga Hridaya")
    
    # Ratings & Merchandising
    rating = models.DecimalField(max_digits=3, decimal_places=1, default=4.6)
    rating_count = models.PositiveIntegerField(default=142)
    is_featured = models.BooleanField(default=False)
    is_bestseller = models.BooleanField(default=False)
    is_kerala_certified = models.BooleanField(default=True)
    
    # Visuals
    image_url = models.CharField(max_length=500, blank=True)
    image_svg_accent = models.CharField(max_length=30, default='#1b5e20') # Color accent for the card/illustration

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-is_bestseller', 'name']

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(f"{self.brand.name}-{self.name}")
            slug = base_slug
            counter = 1
            while Product.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        if self.mrp and self.price and self.mrp > self.price:
            self.discount_percent = int(round(((self.mrp - self.price) / self.mrp) * 100))
        super().save(*args, **kwargs)

    @property
    def is_in_stock(self):
        return self.stock > 0

    @property
    def is_low_stock(self):
        return 0 < self.stock <= self.low_stock_threshold

    @property
    def savings(self):
        return max(0, self.mrp - self.price)

    def __str__(self):
        return f"{self.name} - {self.brand.name} (Stock: {self.stock})"
