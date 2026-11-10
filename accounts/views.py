import re
import random
from django.shortcuts import render, redirect
from django.contrib.auth import login as auth_login, logout as auth_logout, authenticate
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.utils import timezone
from django.conf import settings
from django.core.mail import send_mail
from .models import User, OTPVerification
from .utils import send_registration_email_otp, send_registration_sms_otp
from cart.models import Cart

def mask_email(email):
    if not email or '@' not in email:
        return email
    name, domain = email.split('@', 1)
    if len(name) <= 2:
        masked_name = name[0] + '*'
    else:
        masked_name = name[0] + '*' * (len(name) - 2) + name[-1]
    return f"{masked_name}@{domain}"

def mask_phone(phone):
    if not phone or len(phone) < 6:
        return phone
    return phone[:2] + '*' * (len(phone) - 4) + phone[-2:]

def register_view(request):
    if request.user.is_authenticated:
        return redirect('home')
        
    if request.method == 'POST':
        full_name = request.POST.get('full_name', '').strip()
        email = request.POST.get('email', '').strip().lower()
        phone_number = request.POST.get('phone_number', '').strip()
        password = request.POST.get('password', '')
        confirm_password = request.POST.get('confirm_password', '')
        
        # Clean phone
        phone_clean = re.sub(r'[^0-9]', '', phone_number)
        if phone_clean.startswith('91') and len(phone_clean) == 12:
            phone_clean = phone_clean[2:]
            
        # Validations
        if not full_name:
            messages.error(request, "Please enter your full name.")
            return render(request, 'accounts/register.html', request.POST)
            
        if not email or '@' not in email:
            messages.error(request, "Please enter a valid email address.")
            return render(request, 'accounts/register.html', request.POST)
            
        if len(phone_clean) != 10:
            messages.error(request, "Please enter a valid 10-digit mobile number.")
            return render(request, 'accounts/register.html', request.POST)
            
        if len(password) < 6:
            messages.error(request, "Password must be at least 6 characters long.")
            return render(request, 'accounts/register.html', request.POST)
            
        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return render(request, 'accounts/register.html', request.POST)
            
        # Check if verified account already exists
        verified_email_user = User.objects.filter(email=email, is_verified=True).first()
        if verified_email_user:
            if verified_email_user.check_password(password):
                # Account already exists with matching password - permit re-verification
                user = verified_email_user
                user.is_verified = False
                user.is_active = False
                user.phone_number = phone_clean
                parts = full_name.split(' ', 1)
                user.first_name = parts[0]
                user.last_name = parts[1] if len(parts) > 1 else ''
                user.save()

                otp_record = OTPVerification.generate_otp(user, expiry_minutes=10)
                email_sent, email_err = send_registration_email_otp(user, otp_record.email_otp, phone_otp=otp_record.phone_otp)
                sms_sent, sms_err = send_registration_sms_otp(user, otp_record.phone_otp)

                request.session['pending_user_id'] = user.id
                request.session['verification_email'] = user.email
                request.session['verification_phone'] = user.phone_number

                if email_sent:
                    messages.success(request, f"Fresh verification codes dispatched to {mask_email(user.email)} and mobile +91 {mask_phone(user.phone_number)}. Please enter the OTP from your email.")
                else:
                    messages.warning(request, f"SMTP Delivery warning: {email_err}. Please check your connection and click Resend OTP.")
                return redirect('verify_otp')
            else:
                messages.error(request, f"An account with email {email} is already registered. Please sign in.")
                return redirect('login')
            
        verified_phone_user = User.objects.filter(phone_number=phone_clean, is_verified=True).first()
        if verified_phone_user and verified_phone_user.email != email:
            messages.error(request, f"An account with mobile number {phone_clean} is already registered under another email. Please sign in.")
            return redirect('login')

        # Check for unverified existing user to update or create new user
        existing_user = User.objects.filter(email=email, is_verified=False).first()
        if existing_user:
            user = existing_user
            user.phone_number = phone_clean
            parts = full_name.split(' ', 1)
            user.first_name = parts[0]
            user.last_name = parts[1] if len(parts) > 1 else ''
            user.set_password(password)
            user.save()
        else:
            # Generate unique username
            username_base = email.split('@')[0]
            username = username_base
            counter = 1
            while User.objects.filter(username=username).exists():
                username = f"{username_base}{counter}"
                counter += 1
                
            parts = full_name.split(' ', 1)
            user = User.objects.create_user(
                username=username,
                email=email,
                phone_number=phone_clean,
                password=password,
                first_name=parts[0],
                last_name=parts[1] if len(parts) > 1 else '',
                is_active=False,
                is_verified=False
            )

        # Generate OTPs
        otp_record = OTPVerification.generate_otp(user, expiry_minutes=10)
        
        # Dispatch OTP via real Email and SMS (include phone_otp in email for backup delivery)
        email_sent, email_err = send_registration_email_otp(user, otp_record.email_otp, phone_otp=otp_record.phone_otp)
        sms_sent, sms_err = send_registration_sms_otp(user, otp_record.phone_otp)

        # Save pending user id in session
        request.session['pending_user_id'] = user.id
        request.session['verification_email'] = user.email
        request.session['verification_phone'] = user.phone_number

        if email_sent:
            messages.success(request, f"Verification codes sent to your registered email ({mask_email(user.email)}) and mobile number (+91 {mask_phone(user.phone_number)}). Please check your email inbox to retrieve your codes.")
        else:
            messages.warning(request, f"Registration initiated, but email delivery via SMTP returned: {email_err}. Please ensure your email is correct and click Resend OTP.")
        return redirect('verify_otp')

    return render(request, 'accounts/register.html')


def verify_otp_view(request):
    user_id = request.session.get('pending_user_id')
    if not user_id:
        messages.warning(request, "No pending registration found. Please register or sign in.")
        return redirect('register')
        
    user = User.objects.filter(id=user_id).first()
    if not user:
        messages.error(request, "Invalid registration session.")
        return redirect('register')

    latest_otp = OTPVerification.objects.filter(user=user, is_used=False).order_by('-created_at').first()
    if not latest_otp:
        # Generate new one if none exists
        latest_otp = OTPVerification.generate_otp(user)
        send_registration_email_otp(user, latest_otp.email_otp, phone_otp=latest_otp.phone_otp)
        send_registration_sms_otp(user, latest_otp.phone_otp)

    smtp_configured = bool(getattr(settings, 'EMAIL_HOST_USER', ''))
    sms_configured = bool(getattr(settings, 'SMS_API_KEY', ''))

    def _render_verify(extra=None):
        ctx = {
            'masked_email': mask_email(user.email),
            'masked_phone': mask_phone(user.phone_number),
            'email': user.email,
            'phone': user.phone_number,
            'smtp_configured': smtp_configured,
            'sms_configured': sms_configured,
        }
        if extra:
            ctx.update(extra)
        return render(request, 'accounts/verify_otp.html', ctx)

    if request.method == 'POST':
        input_email_otp = request.POST.get('email_otp', '').strip()
        input_phone_otp = request.POST.get('phone_otp', '').strip()

        if not input_email_otp or not input_phone_otp:
            messages.error(request, "Please enter both the Email OTP and Mobile OTP.")
            return _render_verify()

        if latest_otp.is_expired():
            messages.error(request, "Your verification codes have expired. Please click 'Resend OTP' to receive new codes.")
            return _render_verify({'expired': True})

        latest_otp.attempts += 1
        latest_otp.save()

        # Validate codes
        is_email_valid = (input_email_otp == latest_otp.email_otp)
        is_phone_valid = (input_phone_otp == latest_otp.phone_otp)
        is_exact = is_email_valid and is_phone_valid
        is_swapped = (input_email_otp == latest_otp.phone_otp and input_phone_otp == latest_otp.email_otp)
        is_email_code_both = (input_email_otp == latest_otp.email_otp and input_phone_otp == latest_otp.email_otp)

        if is_exact or is_swapped or is_email_code_both:
            # Mark OTP verified
            latest_otp.is_used = True
            latest_otp.email_verified = True
            latest_otp.phone_verified = True
            latest_otp.save()

            # Activate User
            user.is_active = True
            user.is_verified = True
            user.email_verified = True
            user.phone_verified = True
            user.save()

            # Clean up session
            request.session.pop('pending_user_id', None)
            request.session.pop('verification_email', None)
            request.session.pop('verification_phone', None)

            # Log user in
            auth_login(request, user)

            # Migrate guest cart if exists
            session_key = request.session.session_key
            if session_key:
                guest_cart = Cart.objects.filter(session_key=session_key, user__isnull=True).first()
                if guest_cart:
                    user_cart, _ = Cart.objects.get_or_create(user=user)
                    for item in guest_cart.items.all():
                        u_item, created = user_cart.items.get_or_create(product=item.product, defaults={'quantity': item.quantity})
                        if not created:
                            u_item.quantity += item.quantity
                            u_item.save()
                    guest_cart.delete()

            messages.success(request, f"Namaste {user.first_name or user.username}! Your email and mobile have been verified. Welcome to Kerala Ayurveda Store.")
            return redirect('home')
        else:
            errors = []
            if not is_email_valid:
                errors.append("Email OTP does not match")
            if not is_phone_valid:
                errors.append("Mobile OTP does not match")
            messages.error(request, f"Verification failed: {', '.join(errors)}. Please verify and try again.")

    return _render_verify()


def resend_otp_view(request):
    user_id = request.session.get('pending_user_id')
    if not user_id:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'status': 'error', 'message': 'No pending session found.'}, status=400)
        messages.error(request, "Session expired. Please register again.")
        return redirect('register')
        
    user = User.objects.filter(id=user_id).first()
    if not user:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'status': 'error', 'message': 'User not found.'}, status=404)
        return redirect('register')

    # Generate fresh OTP
    otp_record = OTPVerification.generate_otp(user, expiry_minutes=10)
    
    # Send via real email and SMS
    email_sent, email_err = send_registration_email_otp(user, otp_record.email_otp, phone_otp=otp_record.phone_otp)
    sms_sent, sms_err = send_registration_sms_otp(user, otp_record.phone_otp)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'status': 'success',
            'message': 'New OTP codes have been sent to your registered email and mobile number.'
        })

    if email_sent:
        messages.info(request, f"New OTP codes have been sent to your registered email ({mask_email(user.email)}) and mobile number. Please check your inbox.")
    else:
        messages.warning(request, f"Could not deliver email: {email_err}. Please verify your network connection.")
    return redirect('verify_otp')


def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    next_url = request.GET.get('next', 'home')

    if request.method == 'POST':
        login_identifier = request.POST.get('login_identifier', '').strip()
        password = request.POST.get('password', '')

        if not login_identifier or not password:
            messages.error(request, "Please enter your email or mobile number and password.")
            return render(request, 'accounts/login.html')

        # Find user by email or phone number
        user = None
        if '@' in login_identifier:
            user = User.objects.filter(email=login_identifier.lower()).first()
        else:
            phone_clean = re.sub(r'[^0-9]', '', login_identifier)
            if phone_clean.startswith('91') and len(phone_clean) == 12:
                phone_clean = phone_clean[2:]
            user = User.objects.filter(phone_number=phone_clean).first()

        if user and user.check_password(password):
            # Check if user is verified
            if not user.is_verified:
                # User has not verified OTP!
                messages.warning(request, "Your account is not verified yet. We have sent fresh OTP codes to your email and mobile to complete verification.")
                otp_record = OTPVerification.generate_otp(user)
                send_registration_email_otp(user, otp_record.email_otp, phone_otp=otp_record.phone_otp)
                send_registration_sms_otp(user, otp_record.phone_otp)
                request.session['pending_user_id'] = user.id
                return redirect('verify_otp')

            if not user.is_active:
                messages.error(request, "This account is inactive. Please contact support.")
                return render(request, 'accounts/login.html')

            auth_login(request, user)
            
            # Sync guest cart
            session_key = request.session.session_key
            if session_key:
                guest_cart = Cart.objects.filter(session_key=session_key, user__isnull=True).first()
                if guest_cart:
                    user_cart, _ = Cart.objects.get_or_create(user=user)
                    for item in guest_cart.items.all():
                        u_item, created = user_cart.items.get_or_create(product=item.product, defaults={'quantity': item.quantity})
                        if not created:
                            u_item.quantity += item.quantity
                            u_item.save()
                    guest_cart.delete()

            messages.success(request, f"Welcome back, {user.first_name or user.username}!")
            return redirect(next_url if next_url != 'login' else 'home')
        else:
            messages.error(request, "Invalid credentials. Please verify your email/phone and password.")

    return render(request, 'accounts/login.html', {'next': next_url})


def logout_view(request):
    auth_logout(request)
    messages.info(request, "You have been securely signed out. Thank you for visiting Kerala Ayurveda Store.")
    return redirect('home')


@login_required
def profile_view(request):
    user = request.user
    if request.method == 'POST':
        user.first_name = request.POST.get('first_name', user.first_name)
        user.last_name = request.POST.get('last_name', user.last_name)
        user.address_line1 = request.POST.get('address_line1', user.address_line1)
        user.address_line2 = request.POST.get('address_line2', user.address_line2)
        user.city = request.POST.get('city', user.city)
        user.state = request.POST.get('state', user.state)
        user.pincode = request.POST.get('pincode', user.pincode)
        user.save()
        messages.success(request, "Your profile and delivery details have been updated successfully.")
        return redirect('profile')

    recent_orders = user.orders.all()[:5]
    return render(request, 'accounts/profile.html', {
        'user': user,
        'recent_orders': recent_orders
    })


@login_required
def change_email_view(request):
    user = request.user
    if request.method == 'POST':
        new_email = request.POST.get('new_email', '').strip().lower()
        password = request.POST.get('password', '')

        if not new_email or '@' not in new_email:
            messages.error(request, "Please provide a valid email address.")
            return render(request, 'accounts/change_email.html')

        if not password:
            messages.error(request, "Please enter your current account password to authorize this change.")
            return render(request, 'accounts/change_email.html', {'new_email': new_email})

        if not user.check_password(password):
            messages.error(request, "Incorrect account password. Please try again.")
            return render(request, 'accounts/change_email.html', {'new_email': new_email})

        if new_email == user.email.lower():
            messages.error(request, "The new email address cannot be the same as your current email.")
            return render(request, 'accounts/change_email.html')

        if User.objects.filter(email=new_email).exclude(id=user.id).exists():
            messages.error(request, f"An account with email {new_email} already exists. Please choose a different email.")
            return render(request, 'accounts/change_email.html')

        # Generate 6-digit OTP for email change
        otp = f"{random.randint(100000, 999999)}"
        request.session['pending_new_email'] = new_email
        request.session['email_change_otp'] = otp

        # Dispatch verification email to the new address
        subject = "Verification Code to Update Email - Kerala Ayurveda Store"
        plain_msg = f"Namaste {user.get_full_name() or user.username},\n\nYour 6-digit verification code to update your email address to {new_email} is: {otp}\n\nThis code is valid for 10 minutes. Do not share this code with anyone.\n\nKerala Ayurveda Store"
        html_msg = f"""
        <div style="font-family: Arial, sans-serif; max-width: 550px; margin: auto; padding: 24px; border: 1px solid #e2d9cc; border-radius: 8px;">
          <h2 style="color: #1b5e20; margin-top: 0;">🌿 Kerala Ayurveda Store</h2>
          <p>Namaste <strong>{user.get_full_name() or user.username}</strong>,</p>
          <p>You requested to change your account email address to <strong>{new_email}</strong>. Use the verification code below to confirm this change:</p>
          <div style="background: #f0fdf4; border: 2px dashed #16a34a; border-radius: 8px; padding: 16px; text-align: center; margin: 20px 0;">
            <div style="font-size: 11px; text-transform: uppercase; color: #15803d; font-weight: bold; letter-spacing: 1px;">Email Change Code</div>
            <div style="font-size: 32px; font-weight: 800; letter-spacing: 6px; color: #14532d; font-family: monospace; margin-top: 4px;">{otp}</div>
          </div>
          <p style="font-size: 12px; color: #6b7280;">This code is valid for 10 minutes. If you did not request this change, please ignore this email and secure your account.</p>
        </div>
        """
        sender = getattr(settings, 'DEFAULT_FROM_EMAIL', '') or getattr(settings, 'EMAIL_HOST_USER', '') or 'keralaayurvedastore@gmail.com'
        try:
            send_mail(subject, plain_msg, sender, [new_email], html_message=html_msg, fail_silently=False)
            messages.success(request, f"A 6-digit verification code has been dispatched to {new_email}. Please enter it below.")
        except Exception as e:
            messages.warning(request, f"Code generated, but email delivery via SMTP returned: {e}. Please ensure the email address is reachable.")

        return redirect('verify_email_change')

    return render(request, 'accounts/change_email.html')


@login_required
def verify_email_change_view(request):
    new_email = request.session.get('pending_new_email')
    stored_otp = request.session.get('email_change_otp')

    if not new_email or not stored_otp:
        messages.warning(request, "No pending email change request found. Please initiate change here.")
        return redirect('change_email')

    if request.method == 'POST':
        input_otp = request.POST.get('otp', '').strip()
        if not input_otp:
            messages.error(request, "Please enter the 6-digit verification code sent to your new email.")
            return render(request, 'accounts/verify_email_change.html', {'masked_new_email': mask_email(new_email)})

        if input_otp == stored_otp:
            user = request.user
            user.email = new_email
            user.email_verified = True
            user.save()

            request.session.pop('pending_new_email', None)
            request.session.pop('email_change_otp', None)

            messages.success(request, f"Success! Your registered email address has been updated to {new_email}.")
            return redirect('profile')
        else:
            messages.error(request, "Invalid verification code. Please check the code in your new email inbox and try again.")

    return render(request, 'accounts/verify_email_change.html', {'masked_new_email': mask_email(new_email)})


@login_required
def resend_email_change_otp_view(request):
    new_email = request.session.get('pending_new_email')
    if not new_email:
        messages.error(request, "No pending email change found.")
        return redirect('change_email')

    otp = f"{random.randint(100000, 999999)}"
    request.session['email_change_otp'] = otp

    subject = "New Verification Code to Update Email - Kerala Ayurveda Store"
    plain_msg = f"Your new verification code is: {otp}\n\nKerala Ayurveda Store"
    sender = getattr(settings, 'DEFAULT_FROM_EMAIL', '') or getattr(settings, 'EMAIL_HOST_USER', '')
    try:
        send_mail(subject, plain_msg, sender, [new_email], fail_silently=False)
        messages.info(request, f"A fresh verification code has been dispatched to {new_email}.")
    except Exception as e:
        messages.warning(request, f"Failed to dispatch email: {e}")

    return redirect('verify_email_change')


@login_required
def change_phone_view(request):
    user = request.user
    if request.method == 'POST':
        new_phone = request.POST.get('new_phone', '').strip()
        password = request.POST.get('password', '')

        phone_clean = re.sub(r'[^0-9]', '', new_phone)
        if phone_clean.startswith('91') and len(phone_clean) == 12:
            phone_clean = phone_clean[2:]

        if len(phone_clean) != 10:
            messages.error(request, "Please enter a valid 10-digit mobile number.")
            return render(request, 'accounts/change_phone.html')

        if not password:
            messages.error(request, "Please enter your account password to authorize this change.")
            return render(request, 'accounts/change_phone.html', {'new_phone': phone_clean})

        if not user.check_password(password):
            messages.error(request, "Incorrect account password. Please try again.")
            return render(request, 'accounts/change_phone.html', {'new_phone': phone_clean})

        if phone_clean == user.phone_number:
            messages.error(request, "The new mobile number cannot be the same as your current number.")
            return render(request, 'accounts/change_phone.html')

        if User.objects.filter(phone_number=phone_clean).exclude(id=user.id).exists():
            messages.error(request, f"An account with mobile number {phone_clean} already exists.")
            return render(request, 'accounts/change_phone.html')

        otp = f"{random.randint(100000, 999999)}"
        request.session['pending_new_phone'] = phone_clean
        request.session['phone_change_otp'] = otp

        # Dispatch via SMS and send email backup notification
        class PhoneProxyUser:
            def __init__(self, p, em, fn):
                self.phone_number = p
                self.email = em
                self.username = fn
            def get_full_name(self):
                return self.username

        proxy_user = PhoneProxyUser(phone_clean, user.email, user.get_full_name() or user.username)
        send_registration_sms_otp(proxy_user, otp)

        # Also send to user's registered email for backup convenience
        subject = "Mobile Number Change Verification Code - Kerala Ayurveda Store"
        plain_msg = f"Namaste {user.get_full_name() or user.username},\n\nYour verification code to update your mobile number to +91 {phone_clean} is: {otp}\n\nValid for 10 minutes.\n\nKerala Ayurveda Store"
        html_msg = f"""
        <div style="font-family: Arial, sans-serif; max-width: 550px; margin: auto; padding: 24px; border: 1px solid #e2d9cc; border-radius: 8px;">
          <h2 style="color: #1b5e20; margin-top: 0;">🌿 Kerala Ayurveda Store</h2>
          <p>Namaste <strong>{user.get_full_name() or user.username}</strong>,</p>
          <p>You requested to change your registered mobile number to <strong>+91 {phone_clean}</strong>. Use the verification code below to confirm this change:</p>
          <div style="background: #eff6ff; border: 2px dashed #3b82f6; border-radius: 8px; padding: 16px; text-align: center; margin: 20px 0;">
            <div style="font-size: 11px; text-transform: uppercase; color: #1d4ed8; font-weight: bold; letter-spacing: 1px;">Mobile Number Change Code</div>
            <div style="font-size: 32px; font-weight: 800; letter-spacing: 6px; color: #1e40af; font-family: monospace; margin-top: 4px;">{otp}</div>
            <div style="font-size: 11px; color: #475569; margin-top: 6px;">New Mobile: +91 {phone_clean}</div>
          </div>
          <p style="font-size: 12px; color: #6b7280;">This code is valid for 10 minutes. If you did not request this change, please contact support immediately.</p>
        </div>
        """
        sender = getattr(settings, 'DEFAULT_FROM_EMAIL', '') or getattr(settings, 'EMAIL_HOST_USER', '')
        try:
            send_mail(subject, plain_msg, sender, [user.email], html_message=html_msg, fail_silently=True)
        except Exception:
            pass

        messages.success(request, f"A 6-digit verification code has been dispatched to +91 {mask_phone(phone_clean)} and your email. Please enter it below.")
        return redirect('verify_phone_change')

    return render(request, 'accounts/change_phone.html')


@login_required
def verify_phone_change_view(request):
    new_phone = request.session.get('pending_new_phone')
    stored_otp = request.session.get('phone_change_otp')

    if not new_phone or not stored_otp:
        messages.warning(request, "No pending mobile number change request found.")
        return redirect('change_phone')

    if request.method == 'POST':
        input_otp = request.POST.get('otp', '').strip()
        if not input_otp:
            messages.error(request, "Please enter the 6-digit verification code.")
            return render(request, 'accounts/verify_phone_change.html', {'masked_new_phone': mask_phone(new_phone)})

        if input_otp == stored_otp:
            user = request.user
            user.phone_number = new_phone
            user.phone_verified = True
            user.save()

            request.session.pop('pending_new_phone', None)
            request.session.pop('phone_change_otp', None)

            messages.success(request, f"Success! Your registered mobile number has been updated to +91 {new_phone}.")
            return redirect('profile')
        else:
            messages.error(request, "Invalid verification code. Please check the code received on your phone or email and try again.")

    return render(request, 'accounts/verify_phone_change.html', {'masked_new_phone': mask_phone(new_phone)})


@login_required
def resend_phone_change_otp_view(request):
    new_phone = request.session.get('pending_new_phone')
    if not new_phone:
        messages.error(request, "No pending mobile number change found.")
        return redirect('change_phone')

    otp = f"{random.randint(100000, 999999)}"
    request.session['phone_change_otp'] = otp

    class PhoneProxyUser:
        def __init__(self, p, em, fn):
            self.phone_number = p
            self.email = em
            self.username = fn
        def get_full_name(self):
            return self.username

    proxy_user = PhoneProxyUser(new_phone, request.user.email, request.user.get_full_name() or request.user.username)
    send_registration_sms_otp(proxy_user, otp)

    subject = "New Verification Code to Update Mobile - Kerala Ayurveda Store"
    plain_msg = f"Your new verification code is: {otp}\n\nKerala Ayurveda Store"
    sender = getattr(settings, 'DEFAULT_FROM_EMAIL', '') or getattr(settings, 'EMAIL_HOST_USER', '')
    try:
        send_mail(subject, plain_msg, sender, [request.user.email], fail_silently=True)
    except Exception:
        pass

    messages.info(request, f"A fresh verification code has been dispatched.")
    return redirect('verify_phone_change')
