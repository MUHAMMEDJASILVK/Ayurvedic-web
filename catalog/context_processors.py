from catalog.models import Category, Brand

def portal_context(request):
    try:
        categories = Category.objects.all().order_by('display_order', 'name')
        brands = Brand.objects.all().order_by('name')
    except Exception:
        categories = []
        brands = []
    
    return {
        'nav_categories': categories,
        'nav_brands': brands,
        'portal_brand_name': 'Kerala Ayurveda Store',
        'portal_brand_tagline': 'Authentic Traditional Herbal Formulations',
    }
