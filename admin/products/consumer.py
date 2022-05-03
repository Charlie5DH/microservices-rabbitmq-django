import pika

# create connection parameters
params = pika.URLParameters('amqp://root:root@localhost:5672/')
# create connection
connection = pika.BlockingConnection(params)
channel = connection.channel()

# declare a queue
channel.queue_declare(queue='admin')

def callback(ch, method, properties, body):
    print(f"Received in queue admin -> [x] -> Received {body}")

channel.basic_consume(on_message_callback=callback, queue='admin', auto_ack=False)

print("Starting consumer")
channel.start_consuming()

# this deletes the queue
#channel.close()