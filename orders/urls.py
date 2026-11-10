from django.urls import path
from . import views

urlpatterns = [
    path('checkout/', views.checkout_view, name='checkout'),
    path('place-order/', views.place_order_view, name='place_order'),
    path('success/<str:order_number>/', views.order_success_view, name='order_success'),
    path('history/', views.order_history_view, name='order_history'),
    path('detail/<str:order_number>/', views.order_detail_view, name='order_detail'),
    path('cancel/<str:order_number>/', views.cancel_order_view, name='cancel_order'),
    path('invoice/<str:order_number>/', views.invoice_view, name='invoice'),
]

