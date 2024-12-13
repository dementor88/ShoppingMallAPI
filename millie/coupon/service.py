from math import ceil
from .models import Coupon
from .serializers import CouponSerializer
from ..settings import PAGE_SIZE


class CouponService:
    def get_active_coupons(self, include_inactive=0, page=1, page_size=PAGE_SIZE, order_by=None, asc=0):
        # lazy-query
        if include_inactive == 1:
            coupons = Coupon.objects.all()
        else:
            coupons = Coupon.objects.filter(active=True)

        if ((order_by is not None and order_by != 'uploaded_at') or
                (asc is not None and asc > 0)):
            order_field = order_by or 'uploaded_at'
            ascending = asc or 0
            if ascending == 0:
                order_field = '-' + order_field
            coupons = coupons.order_by(order_field)

        # implement pagination
        total_count = coupons.count()
        start = (page - 1) * page_size
        end = start + page_size
        total_pages = ceil(total_count / page_size)
        coupons = coupons[start:end]

        serializer = CouponSerializer(coupons, many=True)
        coupons_data = {
            'total_count': total_count,
            'total_pages': total_pages,
            'current_page': page,
            'page_size': page_size,
            'coupons': serializer.data
        }

        return coupons_data