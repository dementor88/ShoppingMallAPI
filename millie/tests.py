from django.db import IntegrityError
from django.test import TestCase
from django.core.cache import cache
from rest_framework.test import APIClient
from rest_framework import status
from .coupon.models import Coupon
from .product.models import Product, Category


class ShoppingAPITestCase(TestCase):
    def setUp(self):
        # Set 3 categories
        self.category_1 = Category.objects.create(name='Electronics')
        self.category_2 = Category.objects.create(name='Book')
        self.category_3 = Category.objects.create(name='Misc')

        # Set 2 Electronics product
        self.product_1 = Product.objects.create(
            name='Smartphone',
            description='long lost old LG smartphone',
            price=500000,
            category=self.category_1,
            discount_rate=0.1,
            coupon_applicable=True
        )
        self.product_2 = Product.objects.create(
            name='Computer',
            description='Latest high speed computer',
            price=1200000,
            category=self.category_1,
            discount_rate=0.05,
            coupon_applicable=False
        )
        # Set 1 Book product
        self.product_3 = Product.objects.create(
            name='Bible',
            description='The most popular novel in the world',
            price=7000,
            category=self.category_2,
            discount_rate=0.3,
            coupon_applicable=True
        )
        # Set 1 Misc product
        self.product_4 = Product.objects.create(
            name='25 cent',
            description='A quarter coin of USA currency',
            price=1000,
            category=self.category_3,
            discount_rate=0.5,
            coupon_applicable=False
        )

        # Set 2 coupons
        self.coupon_1 = Coupon.objects.create(code='DISCOUNT10', discount_rate=0.1)
        self.coupon_2 = Coupon.objects.create(code='DISCOUNT90', discount_rate=0.9)

        self.client = APIClient()

    def test_product_discount_rate_policy(self):
        with self.assertRaises(IntegrityError):
            # Create wrong product
            Product.objects.create(
                name='Minus',
                description='Discount rate with minus value',
                price=100,
                category=self.category_3,
                discount_rate=-0.5,
                coupon_applicable=False
            )

    def test_coupon_discount_rate_policy(self):
        with self.assertRaises(IntegrityError):
            # Create wrong coupon
            Coupon.objects.create(code='OVER1.0', discount_rate=1.1)

    def test_get_products(self):
        # Test retrieving all products
        response = self.client.get('/product/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        fields_2_return = {'id', 'name', 'description', 'price', 'category', 'discount_rate', 'coupon_applicable'}
        self.assertEqual(set(response.json()[0].keys()), fields_2_return)
        # 'category' field returns {'id': ..., 'name': ...}
        self.assertIn('id', response.json()[0]['category'])
        self.assertIn('name', response.json()[0]['category'])
        # all products are 4
        self.assertEqual(len(response.json()), 4)

    def test_get_products_by_category(self):
        # Test retrieving products filtered by category
        response = self.client.get(f'/product/?category_id={self.category_1.id}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # all products filtered by category_1 are 2
        self.assertEqual(len(response.json()), 2)

    def test_get_product_detail(self):
        # Test retrieving product detail
        response = self.client.get(f'/product/{self.product_1.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('final_price', response.json())
        self.assertEqual(response.json()['final_price'], int(self.product_1.price * (1 - self.product_1.discount_rate)))

    def test_get_product_detail_with_coupon(self):
        # Test retrieving product detail with a valid coupon
        response = self.client.get(f'/product/{self.product_1.id}/?coupon_code={self.coupon_1.code}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        expected_price = int(self.product_1.price * (1 - (self.product_1.discount_rate + self.coupon_1.discount_rate)))
        self.assertEqual(response.json()['final_price'], expected_price)

    def test_get_product_detail_with_invalid_coupon(self):
        # Test retrieving product detail with an invalid coupon
        response = self.client.get(f'/product/{self.product_1.id}/?coupon_code=INVALID')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_available_coupons(self):
        # Test retrieving available coupons for a product
        response = self.client.get(f'/coupon/available/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()), 2)

    def test_cache_invalidation(self):
        # cache empty
        all_products_cache_key = f'products_all'
        products_by_category_cache_key = f'products_{self.product_1.category_id}'
        product_detail_cache_key = f'product_detail_{self.product_1.id}'
        assert cache.get(all_products_cache_key) is None
        assert cache.get(products_by_category_cache_key) is None
        assert cache.get(product_detail_cache_key) is None

        # all_products_cache_key filled
        response = self.client.get('/product/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        assert cache.get(all_products_cache_key) is not None

        # products_by_category_cache_key
        response = self.client.get(f'/product/?category_id={self.category_1.id}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        assert cache.get(products_by_category_cache_key) is not None

        # product_detail_cache_key filled
        response =self.client.get(f'/product/{self.product_1.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        assert cache.get(product_detail_cache_key) is not None

        # cache invalidate after instance saved
        self.product_1.price = self.product_1.price + 1000
        self.product_1.save()
        assert cache.get(all_products_cache_key) is None
        assert cache.get(products_by_category_cache_key) is None
        assert cache.get(product_detail_cache_key) is None

    def test_update_category(self):
        # cache empty
        category_cache_key = f'category_{self.category_1.id}'
        new_category_cache_key = f'category_{self.category_2.id}'
        all_products_cache_key = f'products_all'
        products_by_category_cache_key = f'products_{self.product_1.category_id}'
        products_by_new_category_cache_key = f'products_{self.product_1.category_id}'
        product_detail_cache_key = f'product_detail_{self.product_1.id}'
        assert cache.get(category_cache_key) is None
        assert cache.get(new_category_cache_key) is None
        assert cache.get(all_products_cache_key) is None
        assert cache.get(products_by_category_cache_key) is None
        assert cache.get(products_by_new_category_cache_key) is None
        assert cache.get(product_detail_cache_key) is None

        # all_products_cache_key filled
        response = self.client.get('/product/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        assert cache.get(all_products_cache_key) is not None

        # products_by_category_cache_key
        response = self.client.get(f'/product/?category_id={self.category_1.id}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()), 2)
        assert cache.get(products_by_category_cache_key) is not None
        response = self.client.get(f'/product/?category_id={self.category_2.id}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()), 1)
        assert cache.get(products_by_new_category_cache_key) is not None

        # product_detail_cache_key filled
        response =self.client.get(f'/product/{self.product_1.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        assert cache.get(product_detail_cache_key) is not None

        assert cache.get(category_cache_key) is not None
        assert cache.get(new_category_cache_key) is not None

        # change category_id of product_1
        self.product_1.update_category(self.category_2.id)
        # all related cache should be invalidated
        assert cache.get(category_cache_key) is None
        assert cache.get(new_category_cache_key) is None
        assert cache.get(all_products_cache_key) is None
        assert cache.get(products_by_category_cache_key) is None
        assert cache.get(products_by_new_category_cache_key) is None
        assert cache.get(product_detail_cache_key) is None

        # product count by category is changed
        response = self.client.get(f'/product/?category_id={self.category_1.id}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()), 1)
        response = self.client.get(f'/product/?category_id={self.category_2.id}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()), 2)
