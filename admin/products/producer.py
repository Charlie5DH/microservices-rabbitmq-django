import pika
import json

def publish(method='', exchange='', queue='admin', message='Hello World!'):
    
    # create connection parameters
    params = pika.URLParameters('amqp://root:root@rabbitmq:5672/')
    # create connection
    connection = pika.BlockingConnection(params)
    channel = connection.channel()

    '''
    We're connected now, to a broker on the local machine - hence the localhost. 
    If we wanted to connect to a broker on a different machine we'd simply specify its name or IP address here.

    Next, before sending we need to make sure the recipient queue exists. 
    If we send a message to non-existing location, RabbitMQ will just drop the message. 
    Let's create a queue to which the message will be delivered:
    '''
    channel.basic_qos(prefetch_count=1)
    ## This queue is intentionally non-durable. See http://www.rabbitmq.com/ha.html#non-mirrored-queue-behavior-on-node-failure
    ## to learn more.
    channel.queue_declare(queue=queue, durable=False)
    # The properties of the message so we can discriminate between different types of messages
    properties = pika.BasicProperties(method)
    
    # At this point we're ready to send a message. 
    # In RabbitMQ a message can never be sent directly to the queue, it always needs to go through an exchange. 
    # All we need to know now is how to use a default exchange identified by an empty string.
    # This exchange is special ‒ it allows us to specify exactly to which queue the message should go. 
    # The queue name needs to be specified in the routing_key parameter:

    channel.basic_publish(exchange='', routing_key=queue, body=json.dumps(message), properties=properties)
    print(f" [admin producer] Sent a message: \n `{message}`")


    

# Before exiting the program we need to make sure the network buffers were flushed and our message was actually delivered to RabbitMQ. 
# We can do it by gently closing the connection.
# connection.close()
