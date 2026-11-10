from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import Cart, CartItem
from catalog.models import Product

def _get_or_create_cart(request):
    if not request.session.session_key:
        request.session.create()

    if request.user.is_authenticated:
        cart, _ = Cart.objects.get_or_create(user=request.user)
    else:
        cart, _ = Cart.objects.get_or_create(session_key=request.session.session_key)
    return cart


def cart_view(request):
    cart = _get_or_create_cart(request)
    cart_items = cart.items.select_related('product', 'product__brand').all()
    
    context = {
        'cart': cart,
        'cart_items': cart_items,
    }
    return render(request, 'cart/cart.html', context)


@require_POST
def add_to_cart_view(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart = _get_or_create_cart(request)

    if not product.is_in_stock:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'status': 'error', 'message': f'Sorry, {product.name} is currently out of stock.'}, status=400)
        messages.error(request, f"Sorry, {product.name} is currently out of stock.")
        return redirect('cart')

    try:
        qty = int(request.POST.get('quantity', 1))
    except ValueError:
        qty = 1
    qty = max(1, min(qty, 10))

    item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        defaults={'quantity': qty}
    )

    if not created:
        new_qty = item.quantity + qty
        if new_qty > product.stock:
            new_qty = product.stock
            messages.warning(request, f"Max available stock for {product.name} is {product.stock}.")
        item.quantity = new_qty
        item.save()

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'status': 'success',
            'message': f'"{product.name}" added to cart.',
            'cart_count': cart.total_items,
            'cart_subtotal': float(cart.subtotal_price),
            'item_quantity': item.quantity
        })

    messages.success(request, f'Added "{product.name}" to your cart.')
    next_url = request.POST.get('next')
    if next_url:
        return redirect(next_url)
    return redirect('cart')


@require_POST
def update_cart_item_view(request, item_id):
    cart = _get_or_create_cart(request)
    item = get_object_or_404(CartItem, id=item_id, cart=cart)
    
    action = request.POST.get('action')
    try:
        if action == 'increase':
            if item.quantity < item.product.stock:
                item.quantity += 1
                item.save()
            else:
                messages.warning(request, f"Cannot add more. Only {item.product.stock} units in stock.")
        elif action == 'decrease':
            if item.quantity > 1:
                item.quantity -= 1
                item.save()
            else:
                item.delete()
        elif action == 'set':
            new_qty = int(request.POST.get('quantity', 1))
            if new_qty <= 0:
                item.delete()
            else:
                item.quantity = min(new_qty, item.product.stock)
                item.save()
    except Exception as e:
        messages.error(request, f"Error updating cart: {e}")

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'status': 'success',
            'cart_count': cart.total_items,
            'cart_subtotal': float(cart.subtotal_price),
            'subtotal_mrp': float(cart.subtotal_mrp),
            'discount': float(cart.total_discount),
            'delivery_fee': float(cart.delivery_fee),
            'grand_total': float(cart.grand_total)
        })

    return redirect('cart')


@require_POST
def remove_from_cart_view(request, item_id):
    cart = _get_or_create_cart(request)
    item = get_object_or_404(CartItem, id=item_id, cart=cart)
    product_name = item.product.name
    item.delete()

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'status': 'success',
            'message': f'"{product_name}" removed from cart.',
            'cart_count': cart.total_items,
            'cart_subtotal': float(cart.subtotal_price),
            'grand_total': float(cart.grand_total)
        })

    messages.info(request, f'"{product_name}" has been removed from your cart.')
    return redirect('cart')
