from django.urls import path
from . import views

urlpatterns = [
    path('all/', views.get_active_coupons, name='get_active_coupons'),
]