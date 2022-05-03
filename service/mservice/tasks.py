from __future__ import absolute_import, unicode_literals

from celery import shared_task
import os
import pika
import json
import django
from sys import path
from os import environ
from rest_framework.response import Response
 
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "base.settings")
django.setup()

from .serializers import ProductSerializer

def callback(ch, method, properties, body):
    
    print('Received message from admin')
    data = json.loads(body)
    print(data)

    if properties.content_type == 'product_created':
        serializer = ProductSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            print(f" Saved to database")
    else:
        print(f" Not saved")

@shared_task
def consumer():
    params = pika.URLParameters('amqp://root:root@rabbitmq:5672/')
    connection = pika.BlockingConnection(params)
    channel = connection.channel()

    channel.queue_declare(queue='admin')

    channel.basic_consume(on_message_callback=callback, queue='admin', auto_ack=True)

    try:
        print("Starting consumer")
        channel.start_consuming()
    except KeyboardInterrupt:
        channel.stop_consuming()
        connection.close()
        print("Stopping consumer")
    

# this deletes the queue
#channel.close()