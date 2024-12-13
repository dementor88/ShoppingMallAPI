from django.core.cache import cache
from .models import Coupon
from .serializers import CouponSerializer
from ..settings import CACHE_MAX_TIMEOUT


class CouponService:
    def get_available_coupons(self):
        cache_key = f'available_coupons_all'
        coupons_data = cache.get(cache_key)

        if not coupons_data:
            coupons = Coupon.objects.all()
            coupons_data = CouponSerializer(coupons, many=True).data
            cache.set(cache_key, coupons_data, timeout=CACHE_MAX_TIMEOUT)  # Cache for 5 minutes

        return coupons_data