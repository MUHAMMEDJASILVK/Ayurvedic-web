import random
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from datetime import timedelta

class User(AbstractUser):
    ROLE_CHOICES = (
        ('customer', 'Customer'),
        ('seller', 'Seller / Inventory Manager'),
        ('admin', 'Administrator'),
    )
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15, unique=True, help_text="10-digit mobile number")
    is_verified = models.BooleanField(default=False, help_text="Verified via Email & Phone OTP")
    email_verified = models.BooleanField(default=False)
    phone_verified = models.BooleanField(default=False)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='customer')
    
    # Shipping details
    address_line1 = models.CharField(max_length=255, blank=True)
    address_line2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, default='Kerala')
    pincode = models.CharField(max_length=10, blank=True)
    
    # Use email or username for login
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'phone_number']

    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.email})"


class OTPVerification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='otp_codes')
    email_otp = models.CharField(max_length=6)
    phone_otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    email_verified = models.BooleanField(default=False)
    phone_verified = models.BooleanField(default=False)
    is_used = models.BooleanField(default=False)
    attempts = models.PositiveIntegerField(default=0)

    @classmethod
    def generate_otp(cls, user, expiry_minutes=10):
        # Generate two unique 6-digit random codes
        e_otp = f"{random.randint(100000, 999999)}"
        p_otp = f"{random.randint(100000, 999999)}"
        # Invalidate old unused OTPs
        cls.objects.filter(user=user, is_used=False).update(is_used=True)
        expires = timezone.now() + timedelta(minutes=expiry_minutes)
        return cls.objects.create(
            user=user,
            email_otp=e_otp,
            phone_otp=p_otp,
            expires_at=expires
        )

    def is_expired(self):
        return timezone.now() > self.expires_at

    def __str__(self):
        return f"OTP for {self.user.email} (expires {self.expires_at.strftime('%H:%M:%S')})"
