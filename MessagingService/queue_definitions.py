import json
import pika

connection = pika.BlockingConnection(pika.ConnectionParameters("localhost"))

channel = connection.channel()
EXCHANGE_NAME = "users"
channel.exchange_declare(
    exchange=EXCHANGE_NAME, exchange_type="fanout", durable=True
)
QUEUE_NAME = "users"
created_users = channel.queue_declare(queue=QUEUE_NAME, durable=True)
channel.queue_bind(queue=created_users.method.queue, exchange=EXCHANGE_NAME)

w2a_channel = connection.channel()
API_EXCHANGE = "apis"
w2a_channel.exchange_declare(
    exchange=EXCHANGE_NAME, exchange_type="fanout", durable=True
)
WRAPPER_TO_APP_QUEUE = "apis"
apis = w2a_channel.queue_declare(queue=WRAPPER_TO_APP_QUEUE, durable=True)
w2a_channel.queue_bind(queue=apis.method.queue, exchange=API_EXCHANGE)