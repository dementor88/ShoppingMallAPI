import time

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
        time.sleep(0.1)
        self.product_2 = Product.objects.create(
            name='Computer',
            description='Latest high speed computer',
            price=1200000,
            category=self.category_1,
            discount_rate=0.05,
            coupon_applicable=False
        )
        time.sleep(0.1)
        # Set 1 Book product
        self.product_3 = Product.objects.create(
            name='Bible',
            description='The most popular novel in the world',
            price=7000,
            category=self.category_2,
            discount_rate=0.3,
            coupon_applicable=True
        )
        time.sleep(0.1)
        # Set 3 Misc product
        self.product_4 = Product.objects.create(
            name='25 cent',
            description='A quarter coin of USA currency (+ premium)',
            price=1000,
            category=self.category_3,
            discount_rate=0.5,
            coupon_applicable=False
        )
        time.sleep(0.1)
        self.product_5 = Product.objects.create(
            name='Zebra',
            description='Seller claims it is a real-life zebra',
            price=10000000000,
            category=self.category_3,
            discount_rate=0.0,
            coupon_applicable=False
        )
        time.sleep(0.1)
        self.product_6 = Product.objects.create(
            name='5 cent',
            description='A nickle coin of USA currency (+ premium)',
            price=500,
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
        return_data = response.json()
        self.assertIn('total_count', return_data)
        self.assertIn('total_pages', return_data)
        self.assertIn('current_page', return_data)

        fields_2_return = {'id', 'name', 'description', 'price', 'category', 'discount_rate', 'coupon_applicable', 'uploaded_at'}
        self.assertEqual(set(return_data['products'][0].keys()), fields_2_return)
        # 'category' field returns {'id': ..., 'name': ...}
        self.assertIn('id', return_data['products'][0]['category'])
        self.assertIn('name', return_data['products'][0]['category'])
        # all products are 6 but returns 5 by pagination
        self.assertEqual(len(return_data['products']), 5)
        self.assertEqual(return_data['total_pages'], 2)

    def test_get_products_pagination(self):
        # Test products pagination function
        response = self.client.get('/product/?page=1&page_size=100')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        return_data = response.json()
        self.assertEqual(return_data['total_pages'], 2)
        self.assertEqual(len(return_data['products']), 5)
        self.assertEqual(return_data['products'][0]['id'], self.product_6.id)

        # search next page
        response = self.client.get('/product/?page=2')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        return_data = response.json()
        self.assertEqual(len(return_data['products']), 1)
        self.assertEqual(return_data['total_pages'], 2)
        self.assertEqual(return_data['products'][0]['id'], self.product_1.id)

        # sort products by name asc
        response = self.client.get('/product/?order_by=name&asc=1')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        return_data = response.json()
        self.assertEqual(return_data['products'][0]['id'], self.product_4.id)

        # sort products by name desc
        response = self.client.get('/product/?order_by=name&asc=0')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        return_data = response.json()
        self.assertEqual(return_data['products'][0]['id'], self.product_5.id)

    def test_get_products_by_category(self):
        # Test retrieving products filtered by category
        response = self.client.get(f'/product/?category_id={self.category_1.id}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        return_data = response.json()
        # all products filtered by category_1 are 2
        self.assertEqual(len(return_data['products']), 2)

    def test_get_product_detail(self):
        # Test retrieving product detail
        response = self.client.get(f'/product/{self.product_1.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        return_data = response.json()
        self.assertIn('final_price', return_data)
        self.assertEqual(return_data['final_price'], int(self.product_1.price * (1 - self.product_1.discount_rate)))

    def test_get_product_detail_with_coupon(self):
        # Test retrieving product detail with a valid coupon
        response = self.client.get(f'/product/{self.product_1.id}/?coupon_code={self.coupon_1.code}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        return_data = response.json()
        expected_price = int(self.product_1.price * (1 - (self.product_1.discount_rate + self.coupon_1.discount_rate)))
        self.assertEqual(return_data['final_price'], expected_price)

    def test_price_with_max_discount(self):
        # Test maximum discount applied to price
        response = self.client.get(f'/product/{self.product_4.id}/?coupon_code={self.coupon_2.code}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        return_data = response.json()
        expected_price = int(self.product_1.price * (1 - (self.product_4.discount_rate + self.coupon_2.discount_rate)))
        self.assertNotEqual(return_data['final_price'], expected_price)
        self.assertNotEqual(return_data['final_price'], 0)

    def test_get_product_detail_with_invalid_coupon(self):
        # Test retrieving product detail with an invalid coupon
        response = self.client.get(f'/product/{self.product_1.id}/?coupon_code=INVALID')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_available_coupons(self):
        # Test retrieving available coupons for a product
        response = self.client.get(f'/coupon/available/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        return_data = response.json()
        self.assertEqual(len(return_data), 2)

    def test_cache_invalidation(self):
        # Test cache invalidation mechanism
        # cache empty
        product_detail_cache_key = f'product_detail_{self.product_1.id}'
        assert cache.get(product_detail_cache_key) is None

        # product_detail_cache_key filled
        response =self.client.get(f'/product/{self.product_1.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        assert cache.get(product_detail_cache_key) is not None

        # cache invalidate after instance update
        self.product_1.price = self.product_1.price + 1000
        self.product_1.save()
        assert cache.get(product_detail_cache_key) is None