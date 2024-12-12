from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from .coupon.models import Coupon
from .product.models import Product, Category

class ShoppingAPITestCase(TestCase):
    def setUp(self):
        # Setting up test data
        self.category = Category.objects.create(name="Electronics")
        self.product = Product.objects.create(
            name="Smartphone",
            description="A smartphone with excellent features",
            price=500000,
            category=self.category,
            discount_rate=0.1,
            coupon_applicable=True
        )
        self.coupon = Coupon.objects.create(code="DISCOUNT10", discount_rate=0.1)

        self.client = APIClient()

    def test_get_products(self):
        # Test retrieving all products
        response = self.client.get('/product/')
        print('response', response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('id', response.json()[0])
        self.assertIn('name', response.json()[0])

    def test_get_products_by_category(self):
        # Test retrieving products filtered by category
        response = self.client.get(f'/product/?category={self.category.id}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()), 1)

    def test_get_product_detail(self):
        # Test retrieving product detail
        response = self.client.get(f'/product/{self.product.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('final_price', response.json())
        self.assertEqual(response.json()['final_price'], int(self.product.price * (1 - self.product.discount_rate)))

    def test_get_product_detail_with_coupon(self):
        # Test retrieving product detail with a valid coupon
        response = self.client.get(f'/product/{self.product.id}/?coupon_code={self.coupon.code}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        expected_price = int(self.product.price * (1 - (self.product.discount_rate + self.coupon.discount_rate)))
        self.assertEqual(response.json()['final_price'], expected_price)

    def test_get_product_detail_with_invalid_coupon(self):
        # Test retrieving product detail with an invalid coupon
        response = self.client.get(f'/product/{self.product.id}/?coupon_code=INVALID')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_available_coupons(self):
        # Test retrieving available coupons for a product
        response = self.client.get(f'/coupon/available/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()), 1)
        self.assertEqual(response.json()[0]['code'], self.coupon.code)
