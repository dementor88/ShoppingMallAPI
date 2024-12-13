from rest_framework import serializers
import pytz
from .models import Category, Product
from ..coupon.models import Coupon
from ..coupon.serializers import CouponSerializer


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']


class ProductSerializer(serializers.ModelSerializer):
    category = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ['id', 'category', 'name', 'price', 'description', 'discount_rate', 'coupon_applicable', 'created_at']

    # get category info (including name)
    def get_category(self, obj):
        try:
            category_data = CategorySerializer(obj.category).data
        except Category.DoesNotExist:
            category_data = None
        return category_data

    # covert model data to JSON
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        # apply commas to price (e.g. 500,000)
        representation['price'] = f'{instance.price:,}원'
        # change float to percent format (e.g. 10%)
        representation['discount_rate'] = f'{round(instance.discount_rate * 100, 2)}%'
        # change UTC to KST
        kst_time = instance.created_at.astimezone(pytz.timezone('Asia/Seoul'))
        representation['created_at'] = kst_time.strftime('%Y년 %m월 %d일 %H시 %M분 %S초')
        return representation


    def to_internal_value(self, data):
        internal_value = super().to_internal_value(data)
        # remove commas from the price field
        if 'price' in data and type(data['price']) != int:
            price_str = data['price'].replace(',', '').replace('원', '')
            internal_value['price'] = int(price_str)
        return internal_value
