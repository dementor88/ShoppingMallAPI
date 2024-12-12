from django.core.cache import cache
from .models import Product, Category
from .serializers import ProductSerializer
from ..coupon.models import Coupon
from ..errors import *
from ..settings import CACHE_MAX_TIMEOUT, CACHE_MIN_TIMEOUT


class ProductService(object):
    def get_products(self, category_id=None):
        cache_key = f'products_{category_id}' if category_id else 'products_all'
        products_data = cache.get(cache_key)

        if not products_data:
            if category_id:
                try:
                    category_id = int(category_id)
                except ValueError:
                    raise TypeError
                products = Product.objects.filter(category_id=category_id).select_related('category')
            else:
                products = Product.objects.all().select_related('category')
            serializer = ProductSerializer(products, many=True)
            products_data = serializer.data
            cache.set(cache_key, products_data, timeout=CACHE_MIN_TIMEOUT)

        return products_data

    def get_product_detail(self, product_id, coupon_code=None):
        cache_key = f"product_detail_{product_id}"
        product_detail = cache.get(cache_key)

        if not product_detail:
            try:
                product = Product.objects.select_related('category').get(id=product_id)
            except Product.DoesNotExist:
                raise ProductDoesNotExist

            coupon = None
            if coupon_code and product.coupon_applicable:
                coupon = Coupon.objects.filter(code=coupon_code).first()
                if not coupon:
                    raise CouponDoesNotExist

            final_price = product.get_final_price(coupon)
            product_detail = ProductSerializer(product).data
            product_detail['final_price'] = final_price
            cache.set(cache_key, product_detail, timeout=CACHE_MAX_TIMEOUT)

        return product_detail