from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('verify-otp/', views.verify_otp_view, name='verify_otp'),
    path('resend-otp/', views.resend_otp_view, name='resend_otp'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    
    # Email Change Flow
    path('change-email/', views.change_email_view, name='change_email'),
    path('verify-email-change/', views.verify_email_change_view, name='verify_email_change'),
    path('resend-email-change-otp/', views.resend_email_change_otp_view, name='resend_email_change_otp'),
    
    # Phone Number Change Flow
    path('change-phone/', views.change_phone_view, name='change_phone'),
    path('verify-phone-change/', views.verify_phone_change_view, name='verify_phone_change'),
    path('resend-phone-change-otp/', views.resend_phone_change_otp_view, name='resend_phone_change_otp'),
]

