from django.urls import path
from . import views

urlpatterns = [
    path('', views.product_list_view, name='home'),
    path('product/<slug:slug>/', views.product_detail_view, name='product_detail'),
    path('api/search-suggest/', views.search_suggest_api, name='search_suggest'),
]

