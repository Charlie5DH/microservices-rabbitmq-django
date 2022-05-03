from rest_framework import serializers
from .models import Product, ProductUser

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'

class ProductUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductUser
        fields = '__all__'