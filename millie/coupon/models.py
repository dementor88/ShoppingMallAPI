from django.db import models
from django.db.models import CheckConstraint, Q

class Coupon(models.Model):
    code = models.CharField(max_length=255, unique=True)
    discount_rate = models.FloatField()
    active = models.BooleanField(default=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-uploaded_at']     # default ordering
        constraints = [
            CheckConstraint(
                check=Q(discount_rate__gte=0.0) & Q(discount_rate__lte=1.0),
                name='coupon_discount_rate_range',
            )
        ]

    def __str__(self):
        return self.code
