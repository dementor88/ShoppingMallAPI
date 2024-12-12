from rest_framework import serializers
from .models import Category, Product
from django.core.cache import cache

from ..settings import CACHE_MAX_TIMEOUT


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']


class ProductSerializer(serializers.ModelSerializer):
    category = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ['id', 'category', 'name', 'price', 'description', 'discount_rate', 'coupon_applicable']

    # get category info (including name)
    def get_category(self, obj):
        cache_key = f'category_{obj.category_id}'
        category_data = cache.get(cache_key)
        if not category_data:
            try:
                category_data = CategorySerializer(obj.category).data
                cache.set(cache_key, category_data, CACHE_MAX_TIMEOUT)
            except Category.DoesNotExist:
                category_data = None
        return category_data

    # covert model data to JSON
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        # apply commas to price (e.g. 500,000)
        representation['price'] = f'{instance.price:,}'
        return representation


    def to_internal_value(self, data):
        internal_value = super().to_internal_value(data)
        # remove commas from the price field
        if 'price' in data and type(data['price']) != int:
            price_str = data['price'].replace(",", "")
            internal_value['price'] = int(price_str)
        return internal_value
