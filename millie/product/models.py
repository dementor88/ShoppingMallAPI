from django.db import models
from django.db.models import CheckConstraint, Q
from ..coupon.models import Coupon
from ..errors import *
import logging

logger = logging.getLogger(__name__)


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.IntegerField()   # assume only Korean Won
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')   # category_obj.products.all() returns all related product objects
    discount_rate = models.FloatField()
    coupon_applicable = models.BooleanField(default=False)
    # Many-to-Many Relationship with Coupon
    coupons = models.ManyToManyField('coupon.Coupon', related_name="products", through="ProductCoupon", blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']     # default ordering
        indexes = [
            models.Index(fields=['created_at', 'name']),  # for pure search by name
            models.Index(fields=['created_at', 'category', 'name']),  # for category filtering, including name search option
        ]
        constraints = [
            CheckConstraint(
                check=Q(discount_rate__gte=0.0) & Q(discount_rate__lte=1.0),
                name='product_discount_rate_range',
            )
        ]

    def __str__(self):
        return self.name

    def get_final_price(self, coupon=None):
        total_discount_rate = self.discount_rate
        if coupon and self.coupon_applicable:
            total_discount_rate += coupon.discount_rate
            total_discount_rate = min(total_discount_rate, 1) # max discount_rate is 1
        final_price = self.price * (1 - total_discount_rate)
        return int(final_price)

class ProductCoupon(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    coupon = models.ForeignKey(Coupon, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('product', 'coupon')

    def __str__(self):
        return f"{self.product.name} - {self.coupon.code}"

