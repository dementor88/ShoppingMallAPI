from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

class Coupon(models.Model):
    code = models.CharField(max_length=255, unique=True)
    discount_rate = models.FloatField(validators=[MinValueValidator(0.0), MaxValueValidator(1.0)])

    def __str__(self):
        return self.code
