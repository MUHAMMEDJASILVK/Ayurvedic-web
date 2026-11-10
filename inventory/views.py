from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Count, Q
from django.http import JsonResponse
from django.core.paginator import Paginator
from catalog.models import Product, Category, Brand
from orders.models import Order, OrderItem
from .models import StockLog

def is_seller_or_admin(user):
    return user.is_authenticated and (user.is_staff or user.role in ['seller', 'admin'] or user.is_superuser)

@login_required
def inventory_dashboard_view(request):
    # Ensure user has seller or admin permissions; if regular customer, offer 1-click switch to Seller Mode for testing!
    if not is_seller_or_admin(request.user):
        if request.GET.get('enable_seller_mode') == '1':
            request.user.role = 'seller'
            request.user.is_staff = True
            request.user.save()
            messages.success(request, "Seller & Inventory Management Mode enabled for your account!")
        else:
            return render(request, 'inventory/access_request.html')

    total_products = Product.objects.count()
    total_stock_units = Product.objects.aggregate(total=Sum('stock'))['total'] or 0
    low_stock_products = Product.objects.filter(stock__gt=0, stock__lte=12).count()
    out_of_stock_products = Product.objects.filter(stock=0).count()

    total_orders = Order.objects.count()
    total_revenue = Order.objects.filter(payment_status='completed').aggregate(total=Sum('grand_total'))['total'] or 0

    recent_orders = Order.objects.prefetch_related('items').order_by('-created_at')[:8]
    critical_stock_items = Product.objects.filter(stock__lte=12).order_by('stock')[:8]
    recent_logs = StockLog.objects.select_related('product', 'performed_by').order_by('-created_at')[:10]

    context = {
        'total_products': total_products,
        'total_stock_units': total_stock_units,
        'low_stock_count': low_stock_products,
        'out_of_stock_count': out_of_stock_products,
        'total_orders': total_orders,
        'total_revenue': total_revenue,
        'recent_orders': recent_orders,
        'critical_stock_items': critical_stock_items,
        'recent_logs': recent_logs,
    }
    return render(request, 'inventory/dashboard.html', context)


@login_required
def stock_list_view(request):
    if not is_seller_or_admin(request.user):
        return redirect('inventory_dashboard')

    products = Product.objects.select_related('category', 'brand').all()

    # Search
    q = request.GET.get('q', '').strip()
    if q:
        products = products.filter(Q(name__icontains=q) | Q(sku__icontains=q) | Q(brand__name__icontains=q))

    # Category filter
    cat_slug = request.GET.get('category', '').strip()
    if cat_slug:
        products = products.filter(category__slug=cat_slug)

    # Status filter
    status = request.GET.get('status', '').strip()
    if status == 'low':
        products = products.filter(stock__gt=0, stock__lte=12)
    elif status == 'out':
        products = products.filter(stock=0)
    elif status == 'in_stock':
        products = products.filter(stock__gt=12)

    # Sorting
    sort_by = request.GET.get('sort', 'stock_asc')
    if sort_by == 'stock_asc':
        products = products.order_by('stock', 'name')
    elif sort_by == 'stock_desc':
        products = products.order_by('-stock', 'name')
    elif sort_by == 'name':
        products = products.order_by('name')
    else:
        products = products.order_by('stock')

    paginator = Paginator(products, 25)
    page_obj = paginator.get_page(request.GET.get('page'))

    categories = Category.objects.all().order_by('name')
    brands = Brand.objects.all().order_by('name')

    context = {
        'products': page_obj,
        'page_obj': page_obj,
        'q': q,
        'cat_slug': cat_slug,
        'status': status,
        'sort_by': sort_by,
        'categories': categories,
        'brands': brands,
    }
    return render(request, 'inventory/stock_list.html', context)


@login_required
def update_stock_view(request, product_id):
    if not is_seller_or_admin(request.user):
        return JsonResponse({'status': 'error', 'message': 'Permission denied.'}, status=403)

    product = get_object_or_404(Product, id=product_id)

    if request.method == 'POST':
        action_type = request.POST.get('action_type', 'add')
        try:
            qty_input = int(request.POST.get('quantity', 0))
        except ValueError:
            qty_input = 0

        old_stock = product.stock
        remarks = request.POST.get('remarks', '').strip()

        if action_type == 'add':
            new_stock = old_stock + qty_input
            change_type = 'restock'
            change_amount = qty_input
        elif action_type == 'deduct':
            new_stock = max(0, old_stock - qty_input)
            change_type = 'damaged'
            change_amount = -(old_stock - new_stock)
        elif action_type == 'set':
            new_stock = max(0, qty_input)
            change_type = 'adjustment'
            change_amount = new_stock - old_stock
        else:
            new_stock = old_stock
            change_type = 'adjustment'
            change_amount = 0

        product.stock = new_stock
        product.save()

        # Log change
        StockLog.objects.create(
            product=product,
            change_type=change_type,
            quantity_changed=change_amount,
            previous_stock=old_stock,
            new_stock=new_stock,
            remarks=remarks or f"Manual stock update ({action_type})",
            performed_by=request.user
        )

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'status': 'success',
                'product_id': product.id,
                'new_stock': product.stock,
                'is_low_stock': product.is_low_stock,
                'is_in_stock': product.is_in_stock,
                'message': f"Stock for {product.name} updated to {product.stock} units."
            })

        messages.success(request, f"Stock for {product.name} updated to {product.stock} units.")
        return redirect('inventory_stock_list')

    return redirect('inventory_stock_list')


@login_required
def order_fulfillment_view(request):
    if not is_seller_or_admin(request.user):
        return redirect('inventory_dashboard')

    orders = Order.objects.prefetch_related('items', 'items__product').all()

    # Search & filters
    q = request.GET.get('q', '').strip()
    if q:
        orders = orders.filter(
            Q(order_number__icontains=q) |
            Q(full_name__icontains=q) |
            Q(email__icontains=q) |
            Q(phone__icontains=q)
        )

    status = request.GET.get('status', '').strip()
    if status:
        orders = orders.filter(order_status=status)

    orders = orders.order_by('-created_at')
    paginator = Paginator(orders, 20)
    page_obj = paginator.get_page(request.GET.get('page'))

    context = {
        'orders': page_obj,
        'page_obj': page_obj,
        'q': q,
        'status': status,
        'status_choices': Order.STATUS_CHOICES,
    }
    return render(request, 'inventory/order_list.html', context)


@login_required
def update_order_status_view(request, order_id):
    if not is_seller_or_admin(request.user):
        return JsonResponse({'status': 'error', 'message': 'Permission denied.'}, status=403)

    order = get_object_or_404(Order, id=order_id)

    if request.method == 'POST':
        new_status = request.POST.get('order_status')
        tracking_num = request.POST.get('tracking_number', '').strip()
        courier = request.POST.get('courier_partner', '').strip()

        if new_status and new_status in dict(Order.STATUS_CHOICES):
            order.order_status = new_status
        if tracking_num:
            order.tracking_number = tracking_num
        if courier:
            order.courier_partner = courier

        order.save()

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'status': 'success',
                'order_status': order.order_status,
                'status_display': order.get_order_status_display(),
                'tracking_number': order.tracking_number,
                'message': f"Order #{order.order_number} status updated to {order.get_order_status_display()}."
            })

        messages.success(request, f"Order #{order.order_number} updated to {order.get_order_status_display()}.")
        return redirect('inventory_orders')

    return redirect('inventory_orders')
