import uuid
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from .models import Order, OrderItem
from cart.models import Cart
from inventory.models import StockLog
from catalog.models import Product

@login_required
def checkout_view(request):
    cart = Cart.objects.filter(user=request.user).first()
    if not cart or cart.total_items == 0:
        messages.warning(request, "Your cart is empty. Please add items to proceed with checkout.")
        return redirect('cart')

    # Verify all items have enough stock before proceeding
    for item in cart.items.all():
        if item.quantity > item.product.stock:
            messages.error(request, f"Cannot proceed: {item.product.name} has only {item.product.stock} units available.")
            return redirect('cart')

    user = request.user
    initial_address = {
        'full_name': user.get_full_name() or user.username,
        'email': user.email,
        'phone': user.phone_number,
        'address_line1': user.address_line1,
        'address_line2': user.address_line2,
        'city': user.city,
        'state': user.state or 'Kerala',
        'pincode': user.pincode,
    }

    context = {
        'cart': cart,
        'cart_items': cart.items.select_related('product', 'product__brand').all(),
        'initial': initial_address,
    }
    return render(request, 'orders/checkout.html', context)


@login_required
def place_order_view(request):
    if request.method != 'POST':
        return redirect('checkout')

    cart = Cart.objects.filter(user=request.user).first()
    if not cart or cart.total_items == 0:
        messages.warning(request, "Your cart is empty.")
        return redirect('cart')

    # Extract delivery details
    full_name = request.POST.get('full_name', '').strip()
    email = request.POST.get('email', '').strip() or request.user.email
    phone = request.POST.get('phone', '').strip() or request.user.phone_number
    address = request.POST.get('address', '').strip()
    city = request.POST.get('city', '').strip()
    state = request.POST.get('state', '').strip() or 'Kerala'
    pincode = request.POST.get('pincode', '').strip()
    landmark = request.POST.get('landmark', '').strip()
    payment_method = request.POST.get('payment_method', 'upi')

    if not full_name or not address or not city or not pincode or not phone:
        messages.error(request, "Please fill in all mandatory delivery address fields.")
        return redirect('checkout')

    # Double check stock availability
    for item in cart.items.all():
        if item.quantity > item.product.stock:
            messages.error(request, f"Insufficient stock for {item.product.name}. Available: {item.product.stock}.")
            return redirect('cart')

    # Save address to profile for future convenience if blank
    user = request.user
    if not user.address_line1:
        user.address_line1 = address
        user.city = city
        user.state = state
        user.pincode = pincode
        user.save()

    # Generate unique order
    order_num = f"KAS-{uuid.uuid4().hex[:8].upper()}"
    total_mrp = cart.subtotal_mrp
    total_discount = cart.total_discount
    delivery_fee = cart.delivery_fee
    grand_total = cart.grand_total

    order = Order.objects.create(
        order_number=order_num,
        user=user,
        full_name=full_name,
        email=email,
        phone=phone,
        shipping_address=address,
        landmark=landmark,
        city=city,
        state=state,
        pincode=pincode,
        total_mrp=total_mrp,
        total_discount=total_discount,
        delivery_fee=delivery_fee,
        grand_total=grand_total,
        payment_method=payment_method,
        payment_status='completed' if payment_method != 'cod' else 'pending',
        transaction_id=f"TXN-{uuid.uuid4().hex[:12].upper()}" if payment_method != 'cod' else 'COD-PENDING',
        order_status='placed',
        tracking_number=f"KP{uuid.uuid4().hex[:9].upper()}IN"
    )

    # Transfer items to OrderItem and decrement inventory stock
    for item in cart.items.all():
        OrderItem.objects.create(
            order=order,
            product=item.product,
            product_name=item.product.name,
            brand_name=item.product.brand.name,
            volume_weight=item.product.volume_weight,
            price=item.product.price,
            mrp=item.product.mrp,
            quantity=item.quantity,
            line_total=item.line_total
        )
        
        # Deduct inventory stock
        prod = item.product
        old_stock = prod.stock
        prod.stock = max(0, prod.stock - item.quantity)
        prod.save()

        # Record Inventory Stock Log
        StockLog.objects.create(
            product=prod,
            change_type='order_deduct',
            quantity_changed=-item.quantity,
            previous_stock=old_stock,
            new_stock=prod.stock,
            reference_id=order.order_number,
            remarks=f"Order deduction by customer {user.email}",
            performed_by=user
        )

    # Empty user's cart
    cart.items.all().delete()

    # Send order confirmation email
    try:
        subject = f"Order Confirmation #{order.order_number} - Kerala Ayurveda Store"
        message = f"Namaste {order.full_name},\n\nYour order #{order.order_number} has been placed successfully!\nTotal Amount: INR {order.grand_total}\nDelivery To: {order.shipping_address}, {order.city} - {order.pincode}\nEstimated Delivery: 3-5 Business Days via Kerala Express.\n\nThank you for choosing authentic Kerala Ayurveda."
        send_mail(
            subject=subject,
            message=message,
            from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'keralaayurvedastore@gmail.com'),
            recipient_list=[order.email],
            fail_silently=True
        )
    except Exception as e:
        print(f"Could not send order confirmation email: {e}")

    messages.success(request, f"Your order #{order.order_number} has been confirmed successfully!")
    return redirect('order_success', order_number=order.order_number)


@login_required
def order_success_view(request, order_number):
    order = get_object_or_404(Order.objects.prefetch_related('items'), order_number=order_number, user=request.user)
    return render(request, 'orders/order_success.html', {'order': order})


@login_required
def order_history_view(request):
    orders = Order.objects.filter(user=request.user).prefetch_related('items').order_by('-created_at')
    return render(request, 'orders/order_history.html', {'orders': orders})


@login_required
def order_detail_view(request, order_number):
    # Sellers/admins can view any order, customer can view their own
    if request.user.role in ['seller', 'admin'] or request.user.is_staff:
        order = get_object_or_404(Order.objects.prefetch_related('items'), order_number=order_number)
    else:
        order = get_object_or_404(Order.objects.prefetch_related('items'), order_number=order_number, user=request.user)
        
    return render(request, 'orders/order_detail.html', {'order': order})


@login_required
def invoice_view(request, order_number):
    if request.user.role in ['seller', 'admin'] or request.user.is_staff:
        order = get_object_or_404(Order.objects.prefetch_related('items'), order_number=order_number)
    else:
        order = get_object_or_404(Order.objects.prefetch_related('items'), order_number=order_number, user=request.user)
        
    return render(request, 'orders/invoice.html', {'order': order})
