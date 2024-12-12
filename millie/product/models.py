from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.IntegerField()   # assume only Korean Won
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    discount_rate = models.FloatField()     #TODO: need to force lower than 1 bigger than 0
    coupon_applicable = models.BooleanField()
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-uploaded_at']     # default ordering
        indexes = [
            models.Index(fields=['uploaded_at', 'name']),  # for pure search by name
            models.Index(fields=['uploaded_at', 'category', 'name']),  # for category filtering, including name search option
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


