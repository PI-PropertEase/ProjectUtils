import json
import pika

from ProjectUtils.MessagingService.schemas import Service

# 1 unica Topic Exchange, que dá para endereçar só para 1 queue ou para muitas (e todas)
#
#       - QUEUE "users" - ligação UserService -> PropertyService, para quando é criado um user
#       - QUEUE "wrapper_events" - ligação wrappers -> PropertyService/CalendarService, para quando
# queremos passar dados de wrappers para esses serviços (importar propriedades, registar uma reservation nova)
#
#       Outras queues: os wrappers vão ter cada um a sua propria queue, para poderem receber mensagens destinadas
# unicamente para eles (por exemplo, quando queremos pedir ao wrapper Zooking para importar as propriedades de
# um certo user), e vão ser eles a declarar essa queue.

## Para enviar mensagens para os destinatários que queremos, usar as routing keys, por exemplo:

#
# def publish_new_user(user: UserBase):
#     channel.basic_publish(
#         exchange=EXCHANGE_NAME,
#         routing_key=USER_QUEUE_ROUTING_KEY, # <------ AQUI!!
#         body=to_json(MessageFactory.create_user_message(MessageType.USER_CREATE, user)),
#         properties=pika.BasicProperties(delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE),
#     )
#
#

connection = pika.BlockingConnection(pika.ConnectionParameters("rabbit_mq"))

channel = connection.channel()
EXCHANGE_NAME = "propertease.topic"
channel.exchange_declare(exchange=EXCHANGE_NAME, exchange_type="topic", durable=True)

USER_QUEUE_NAME = "users"
USER_QUEUE_ROUTING_KEY = "users"
created_users = channel.queue_declare(queue=USER_QUEUE_NAME, durable=True)
channel.queue_bind(
    queue=created_users.method.queue,
    exchange=EXCHANGE_NAME,
    routing_key=USER_QUEUE_ROUTING_KEY,
)

WRAPPER_TO_APP_QUEUE = "wrapper_events"
WRAPPER_TO_APP_ROUTING_KEY = "wrapper_events"
wrapper_events = channel.queue_declare(queue=WRAPPER_TO_APP_QUEUE, durable=True)
channel.queue_bind(
    queue=wrapper_events.method.queue, exchange=EXCHANGE_NAME, routing_key=WRAPPER_TO_APP_ROUTING_KEY
)
# publish to this routing key if you want all wrappers to receive it
WRAPPER_BROADCAST_ROUTING_KEY = "wrappers.all"
WRAPPER_ZOOKING_ROUTING_KEY = "wrappers.zooking"
WRAPPER_CLICKANDGO_ROUTING_KEY = "wrappers.clickandgo"
WRAPPER_EARTHSTAYIN_ROUTING_KEY = "wrappers.earthstayin"

WRAPPER_TO_CALENDAR_QUEUE = "wrapper_events_calendar"
WRAPPER_TO_CALENDAR_ROUTING_KEY = "wrapper_events_calendar"
wrapper_events = channel.queue_declare(queue=WRAPPER_TO_CALENDAR_QUEUE, durable=True)
channel.queue_bind(
    queue=wrapper_events.method.queue, exchange=EXCHANGE_NAME, routing_key=WRAPPER_TO_CALENDAR_ROUTING_KEY
)

# Routing key by service
routing_key_by_service = {
    Service.ZOOKING.value: WRAPPER_ZOOKING_ROUTING_KEY,
    Service.CLICKANDGO.value: WRAPPER_CLICKANDGO_ROUTING_KEY,
    Service.EARTHSTAYIN.value: WRAPPER_EARTHSTAYIN_ROUTING_KEY
}

PROPERTY_TO_ANALYTICS_QUEUE_NAME = "property_analytics"
PROPERTY_TO_ANALYTICS_QUEUE_ROUTING_KEY = "property_analytics"
property_to_analytics = channel.queue_declare(queue=PROPERTY_TO_ANALYTICS_QUEUE_NAME, durable=True)
channel.queue_bind(
    queue=property_to_analytics.method.queue,
    exchange=EXCHANGE_NAME,
    routing_key=PROPERTY_TO_ANALYTICS_QUEUE_ROUTING_KEY,
)

ANALYTICS_TO_PROPERTY_QUEUE_NAME = "analytics_property"
ANALYTICS_TO_PROPERTY_QUEUE_ROUTING_KEY = "analytics_property"
analytics_to_property = channel.queue_declare(queue=ANALYTICS_TO_PROPERTY_QUEUE_NAME, durable=True)
channel.queue_bind(
    queue=analytics_to_property.method.queue,
    exchange=EXCHANGE_NAME,
    routing_key=ANALYTICS_TO_PROPERTY_QUEUE_ROUTING_KEY,
)

PROPERTY_TO_ANALYTICS_DATA_QUEUE_NAME = "property_analytics_data"
PROPERTY_TO_ANALYTICS_DATA_ROUTING_KEY = "property_analytics_data"
property_to_analytics_data = channel.queue_declare(queue=PROPERTY_TO_ANALYTICS_DATA_QUEUE_NAME, durable=True)
channel.queue_bind(
    queue=property_to_analytics_data.method.queue,
    exchange=EXCHANGE_NAME,
    routing_key=PROPERTY_TO_ANALYTICS_DATA_ROUTING_KEY,
)