from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from .models import Product, User
import json
import random
from .serializers import ProductSerializer

from .producer import publish

# Create your views here.

@api_view(['GET'])
def get_products(request):
    products = Product.objects.all()
    serializer = ProductSerializer(products, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def get_random_product(request):
    products = Product.objects.all()
    serializer = ProductSerializer(products[random.randint(0, len(products)-1)], many=False)
    return Response(serializer.data)

@api_view(['GET'])
def get_product(request, id):
    product = Product.objects.get(pk=id)
    serializer = ProductSerializer(product, many=False)
    return Response(serializer.data)

@api_view(['GET'])
def get_product_by_title(request, title):
    product = Product.objects.get(title=title)
    serializer = ProductSerializer(product, many=False)
    return Response(serializer.data)

@api_view(['POST'])
def create_product(request):
    serializer = ProductSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        #testing the rabbitmq messaging
        # when a product is created, a message is sent to the queue
        # we are specifying the parameter product_created as an identifier
        # for the consumer to know what type of message it is and discriminate
        publish(method='product_created',exchange='', queue='admin', message=serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def get_random_user(request):
    users = User.objects.all()
    user = random.choice(users)
    return Response({"id": user.id})
