from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
from .models import Category, Brand, Product

def product_list_view(request):
    products = Product.objects.all().select_related('category', 'brand')
    
    # Search Query
    query = request.GET.get('q', '').strip()
    if query:
        products = products.filter(
            Q(name__icontains=query) |
            Q(short_description__icontains=query) |
            Q(description__icontains=query) |
            Q(ingredients__icontains=query) |
            Q(key_benefits__icontains=query) |
            Q(classical_reference__icontains=query) |
            Q(brand__name__icontains=query) |
            Q(category__name__icontains=query)
        )

    # Category filter
    category_slug = request.GET.get('category', '').strip()
    current_category = None
    if category_slug:
        current_category = Category.objects.filter(slug=category_slug).first()
        if current_category:
            products = products.filter(category=current_category)

    # Brand filter (can be multiple or single)
    selected_brands = request.GET.getlist('brand')
    if selected_brands:
        products = products.filter(brand__slug__in=selected_brands)

    # Product Type filter
    selected_type = request.GET.get('type', '').strip()
    if selected_type:
        products = products.filter(product_type=selected_type)

    # Price range filter
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    if min_price and min_price.isdigit():
        products = products.filter(price__gte=int(min_price))
    if max_price and max_price.isdigit():
        products = products.filter(price__lte=int(max_price))

    # Rating filter
    min_rating = request.GET.get('rating')
    if min_rating:
        try:
            products = products.filter(rating__gte=float(min_rating))
        except ValueError:
            pass

    # Availability / Stock filter
    in_stock_only = request.GET.get('in_stock') == '1'
    if in_stock_only:
        products = products.filter(stock__gt=0)

    # Sorting
    sort_by = request.GET.get('sort', 'featured')
    if sort_by == 'price_low':
        products = products.order_by('price')
    elif sort_by == 'price_high':
        products = products.order_by('-price')
    elif sort_by == 'rating':
        products = products.order_by('-rating', '-rating_count')
    elif sort_by == 'discount':
        products = products.order_by('-discount_percent')
    elif sort_by == 'newest':
        products = products.order_by('-created_at')
    else: # featured / default
        products = products.order_by('-is_bestseller', '-is_featured', 'name')

    total_count = products.count()

    # Pagination: 24 per page for smooth browsing
    paginator = Paginator(products, 24)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Categories and brands for sidebar with counts
    all_categories = Category.objects.all().order_by('display_order', 'name')
    all_brands = Brand.objects.all().order_by('name')

    context = {
        'products': page_obj,
        'page_obj': page_obj,
        'total_count': total_count,
        'query': query,
        'current_category': current_category,
        'category_slug': category_slug,
        'selected_brands': selected_brands,
        'selected_type': selected_type,
        'min_price': min_price or '',
        'max_price': max_price or '',
        'min_rating': min_rating or '',
        'in_stock_only': in_stock_only,
        'sort_by': sort_by,
        'all_categories': all_categories,
        'all_brands': all_brands,
    }
    return render(request, 'catalog/product_list.html', context)


def product_detail_view(request, slug):
    product = get_object_or_404(Product.objects.select_related('category', 'brand'), slug=slug)
    
    # Related products from same category or brand
    related_products = Product.objects.filter(
        category=product.category
    ).exclude(id=product.id).order_by('-rating')[:6]

    context = {
        'product': product,
        'related_products': related_products,
    }
    return render(request, 'catalog/product_detail.html', context)


def search_suggest_api(request):
    q = request.GET.get('q', '').strip()
    if len(q) < 2:
        return JsonResponse({'results': []})

    products = Product.objects.filter(name__icontains=q)[:6]
    brands = Brand.objects.filter(name__icontains=q)[:3]
    categories = Category.objects.filter(name__icontains=q)[:3]

    results = []
    for p in products:
        results.append({
            'type': 'product',
            'title': p.name,
            'subtitle': f"{p.brand.name} • ₹{p.price}",
            'url': f"/product/{p.slug}/"
        })
    for b in brands:
        results.append({
            'type': 'brand',
            'title': b.name,
            'subtitle': 'Kerala Ayurvedic Brand',
            'url': f"/?brand={b.slug}"
        })
    for c in categories:
        results.append({
            'type': 'category',
            'title': c.name,
            'subtitle': 'Category',
            'url': f"/?category={c.slug}"
        })

    return JsonResponse({'results': results})
