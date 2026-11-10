from django.urls import path
from . import views

urlpatterns = [
    path('', views.inventory_dashboard_view, name='inventory_dashboard'),
    path('stock/', views.stock_list_view, name='inventory_stock_list'),
    path('stock/update/<int:product_id>/', views.update_stock_view, name='update_stock'),
    path('orders/', views.order_fulfillment_view, name='inventory_orders'),
    path('orders/update/<int:order_id>/', views.update_order_status_view, name='update_order_status'),
]

