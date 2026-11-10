import re
from django.shortcuts import render, redirect
from django.contrib.auth import login as auth_login, logout as auth_logout, authenticate
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.utils import timezone
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
        verified_email_exists = User.objects.filter(email=email, is_verified=True).exists()
        if verified_email_exists:
            messages.error(request, f"An account with email {email} is already registered. Please sign in.")
            return redirect('login')
            
        verified_phone_exists = User.objects.filter(phone_number=phone_clean, is_verified=True).exists()
        if verified_phone_exists:
            messages.error(request, f"An account with mobile number {phone_clean} is already registered. Please sign in.")
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
        
        # Dispatch OTP via real Email and SMS
        send_registration_email_otp(user, otp_record.email_otp)
        send_registration_sms_otp(user, otp_record.phone_otp)

        # Save pending user id in session
        request.session['pending_user_id'] = user.id
        request.session['verification_email'] = user.email
        request.session['verification_phone'] = user.phone_number

        messages.success(request, "Registration initiated! We have sent a verification code to your registered email and mobile number.")
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
        send_registration_email_otp(user, latest_otp.email_otp)
        send_registration_sms_otp(user, latest_otp.phone_otp)

    if request.method == 'POST':
        input_email_otp = request.POST.get('email_otp', '').strip()
        input_phone_otp = request.POST.get('phone_otp', '').strip()

        if not input_email_otp or not input_phone_otp:
            messages.error(request, "Please enter both the Email OTP and Mobile OTP.")
            return render(request, 'accounts/verify_otp.html', {
                'masked_email': mask_email(user.email),
                'masked_phone': mask_phone(user.phone_number),
                'email': user.email,
                'phone': user.phone_number,
            })

        if latest_otp.is_expired():
            messages.error(request, "Your verification codes have expired. Please click 'Resend OTP' to receive new codes.")
            return render(request, 'accounts/verify_otp.html', {
                'masked_email': mask_email(user.email),
                'masked_phone': mask_phone(user.phone_number),
                'email': user.email,
                'phone': user.phone_number,
                'expired': True
            })

        latest_otp.attempts += 1
        latest_otp.save()

        # Validate codes
        is_email_valid = (input_email_otp == latest_otp.email_otp)
        is_phone_valid = (input_phone_otp == latest_otp.phone_otp)

        if is_email_valid and is_phone_valid:
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

    context = {
        'masked_email': mask_email(user.email),
        'masked_phone': mask_phone(user.phone_number),
        'email': user.email,
        'phone': user.phone_number,
    }
    return render(request, 'accounts/verify_otp.html', context)


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
    send_registration_email_otp(user, otp_record.email_otp)
    send_registration_sms_otp(user, otp_record.phone_otp)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'status': 'success',
            'message': 'New OTP codes have been sent to your registered email and mobile number.'
        })

    messages.info(request, "New OTP codes have been dispatched to your email and mobile number. Please check your inbox and SMS.")
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
                send_registration_email_otp(user, otp_record.email_otp)
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
