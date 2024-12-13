from math import ceil
from django.core.cache import cache
from .models import Product, Category
from .serializers import ProductSerializer
from ..coupon.models import Coupon
from ..coupon.serializers import CouponSerializer
from ..errors import *
from ..settings import CACHE_MAX_TIMEOUT, PAGE_SIZE
import logging

logger = logging.getLogger(__name__)


class ProductService(object):
    def get_products(self,category_id=None, page=1, page_size=PAGE_SIZE, order_by=None, asc=0):
        products = Product.objects.all().prefetch_related('category') # lazy-query
        if category_id:
            try:
                category_id = int(category_id)
            except ValueError:
                logger.error(f'Failed to get products by category_id: {category_id}')
                raise TypeError
            products = Product.objects.filter(category_id=category_id).prefetch_related('category')

        if (order_by is not None and order_by != 'created_at') or (asc is not None and asc > 0):
            order_field = order_by or 'created_at'
            ascending = asc or 0
            if ascending == 0:
                order_field = '-' + order_field
            products = products.order_by(order_field)

        # implement pagination
        total_count = products.count()
        start = (page - 1) * page_size
        end = start + page_size
        total_pages = ceil(total_count / page_size)
        products = products[start:end]

        serializer = ProductSerializer(products, many=True)
        products_data = {
            'total_count': total_count,
            'total_pages': total_pages,
            'current_page': page,
            'page_size': page_size,
            'products': serializer.data
        }

        return products_data

    def get_product_detail(self, product_id, coupon_code=None):
        cache_key = f'product_detail_{product_id}'
        product_detail = cache.get(cache_key)
        if not product_detail:
            try:
                product = Product.objects.prefetch_related('category').get(id=product_id)
            except Product.DoesNotExist:
                logger.error(f'Failed to get product object with product_id: {product_id}')
                raise ProductDoesNotExist

            coupon = None
            if coupon_code and product.coupon_applicable:
                coupon = product.coupons.filter(code=coupon_code, active=True).first()
                if not coupon:
                    logger.error(f'Failed to find coupon object with coupon_code: {coupon_code}')
                    raise CouponDoesNotExist

            final_price = product.get_final_price(coupon)
            product_detail = ProductSerializer(product).data
            product_detail['final_price'] = final_price
            cache.set(cache_key, product_detail, timeout=CACHE_MAX_TIMEOUT)

        return product_detail

    def invalidate_product_cache(self, product_id):
        cache.delete(f'product_detail_{product_id}')

    def get_available_coupons(self, product_id):
        try:
            product = Product.objects.prefetch_related('coupons').get(id=product_id)
        except Product.DoesNotExist:
            raise ProductDoesNotExist

        if not product.coupon_applicable:
            return []

        available_coupons = product.coupons.filter(active=True)
        coupons_data = CouponSerializer(available_coupons, many=True).data
        return coupons_data
