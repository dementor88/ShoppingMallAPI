from django.urls import path
from . import views

urlpatterns = [
    path('all/', views.get_active_coupons, name='get_active_coupons'),
    # path('avaiable/<int:product_id>', views.get_available_coupons, name='get_available_coupons'),
]