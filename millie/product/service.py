from django.core.cache import cache
from .models import Product, Category
from .serializers import ProductSerializer
from ..coupon.models import Coupon
from ..errors import *
from ..settings import CACHE_MAX_TIMEOUT, CACHE_MIN_TIMEOUT
import logging

logger = logging.getLogger(__name__)


class ProductService(object):
    def get_products(self, category_id=None):
        cache_key = f'products_{category_id}' if category_id else 'products_all'
        products_data = cache.get(cache_key)

        if not products_data:
            if category_id:
                try:
                    category_id = int(category_id)
                except ValueError:
                    logger.error(f'Failed to get products by category_id: {category_id}')
                    raise TypeError
                products = Product.objects.filter(category_id=category_id).select_related('category')
            else:
                products = Product.objects.all().select_related('category')
            serializer = ProductSerializer(products, many=True)
            products_data = serializer.data
            cache.set(cache_key, products_data, timeout=CACHE_MIN_TIMEOUT)

        return products_data

    def get_product_detail(self, product_id, coupon_code=None):
        cache_key = f'product_detail_{product_id}'
        product_detail = cache.get(cache_key)
        if not product_detail:
            try:
                product = Product.objects.select_related('category').get(id=product_id)
            except Product.DoesNotExist:
                logger.error(f'Failed to get product object with product_id: {product_id}')
                raise ProductDoesNotExist

            coupon = None
            if coupon_code and product.coupon_applicable:
                coupon = Coupon.objects.filter(code=coupon_code).first()
                if not coupon:
                    logger.error(f'Failed to find coupon object with coupon_code: {coupon_code}')
                    raise CouponDoesNotExist

            final_price = product.get_final_price(coupon)
            product_detail = ProductSerializer(product).data
            product_detail['final_price'] = final_price
            cache.set(cache_key, product_detail, timeout=CACHE_MAX_TIMEOUT)

        return product_detail

    def invalidate_category_cache(self, category_id):
        cache.delete(f'category_{category_id}')
        cache.delete('products_all')
        cache.delete(f'products_{category_id}')

    def invalidate_product_cache(self, product_id, category_id, prev_category_id=None):
        cache.delete(f'product_detail_{product_id}')
        cache.delete('products_all')
        cache.delete(f'products_{category_id}')
        # need to limit updating category field by update_category()
        if prev_category_id:
            cache.delete(f'products_{prev_category_id}')
