from django.db import models

class Coupon(models.Model):
    code = models.CharField(max_length=255, unique=True)
    discount_rate = models.FloatField() #TODO: need to force lower than 1 bigger than 0

    def __str__(self):
        return self.code
