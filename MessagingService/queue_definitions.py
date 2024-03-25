import json
import pika

connection = pika.BlockingConnection(pika.ConnectionParameters("localhost"))
channel = connection.channel()
EXCHANGE_NAME = "users"
QUEUE_NAME = "new_users"
channel.exchange_declare(
    exchange=EXCHANGE_NAME, exchange_type="fanout", durable=True
)
created_users = channel.queue_declare(queue=QUEUE_NAME, durable=True)
channel.queue_bind(queue=created_users.method.queue, exchange=EXCHANGE_NAME)