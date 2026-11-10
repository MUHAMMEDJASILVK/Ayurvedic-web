from cart.models import Cart

def cart_context(request):
    cart_count = 0
    cart_subtotal = 0
    try:
        cart = None
        if request.user.is_authenticated:
            cart = Cart.objects.filter(user=request.user).first()
        elif request.session.session_key:
            cart = Cart.objects.filter(session_key=request.session.session_key).first()
        
        if cart:
            cart_count = cart.total_items
            cart_subtotal = cart.subtotal_price
    except Exception:
        pass
    
    return {
        'cart_item_count': cart_count,
        'cart_subtotal': cart_subtotal,
    }

