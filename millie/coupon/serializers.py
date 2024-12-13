from rest_framework import serializers
import pytz
from .models import Coupon

class CouponSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coupon
        fields = ['id', 'code', 'discount_rate', 'uploaded_at', 'active']

        # covert model data to JSON
        def to_representation(self, instance):
            representation = super().to_representation(instance)
            # change float to percent format (e.g. 10%)
            representation['discount_rate'] = f'{round(instance.discount_rate * 100, 2)}%'
            # change UTC to KST
            kst_time = instance.uploaded_at.astimezone(pytz.timezone('Asia/Seoul'))
            representation['uploaded_at'] = kst_time.strftime('%Y년 %m월 %d일 %H시 %M분 %S초')
            return representation