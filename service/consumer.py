import os
import pika
import json
import django
from sys import path
from os import environ
from rest_framework.response import Response
import time
 
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "base.settings")
django.setup()

from mservice.serializers import ProductSerializer

time.sleep(30) 
# Sleep for 30 seconds, wait for rabbitmq to start
# not the ideal slution, but it works
# i think is better to add the task in celery
# but i don't know how to do it, so, is a TODO

params = pika.URLParameters('amqp://root:root@rabbitmq:5672/')

connection = pika.BlockingConnection(params)
channel = connection.channel()

channel.queue_declare(queue='admin')

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