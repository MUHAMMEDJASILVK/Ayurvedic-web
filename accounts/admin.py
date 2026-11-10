from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, OTPVerification

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'phone_number', 'first_name', 'last_name', 'is_verified', 'role', 'is_staff')
    list_filter = ('is_verified', 'role', 'is_staff', 'is_superuser')
    search_fields = ('username', 'email', 'phone_number', 'first_name', 'last_name')
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Verification & Role', {'fields': ('phone_number', 'is_verified', 'email_verified', 'phone_verified', 'role')}),
        ('Shipping Address', {'fields': ('address_line1', 'address_line2', 'city', 'state', 'pincode')}),
    )

@admin.register(OTPVerification)
class OTPVerificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'email_otp', 'phone_otp', 'created_at', 'expires_at', 'is_used', 'is_expired')
    list_filter = ('is_used', 'created_at')
    search_fields = ('user__email', 'user__phone_number', 'email_otp', 'phone_otp')
