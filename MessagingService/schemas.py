import json
from datetime import datetime
from enum import StrEnum, Enum
from time import time
from pydantic import BaseModel
from typing import Union, Dict, List
from aio_pika import Message


class Service(Enum):
    ZOOKING = "zooking"
    CLICKANDGO = "clickandgo"
    EARTHSTAYIN = "earthstayin"


class BaseMessage:
    def __init__(self, message_type: str, body: dict, ts: float = None):
        self.message_type = message_type
        self.body = body
        self.ts = ts if ts is not None else time()


class MessageType(StrEnum):
    # Messages triggered by user
    USER_CREATE = "user_create"
    USER_DELETE = "user_delete"
    PROPERTY_CREATE = "property_create"
    PROPERTY_UPDATE = "property_update"
    PROPERTY_DELETE = "property_delete"
    MANAGEMENT_EVENT_CREATE = "management_event_create"
    MANAGEMENT_EVENT_UPDATE = "management_event_update"
    MANAGEMENT_EVENT_DELETE = "management_event_delete"
    # UserService request property import from wrappers
    PROPERTY_IMPORT = "property_import"
    RESERVATION_IMPORT_REQUEST = "reservation_import_request"
    # PropertyService requests reservation import from wrappers sending new id if it's a duplicated property
    RESERVATION_IMPORT_INITIAL_REQUEST = "reservation_import_initial_request"
    # Responses from PropertyService to the request
    PROPERTY_IMPORT_RESPONSE = "property_import_response"
    PROPERTY_IMPORT_DUPLICATE = "property_import_duplicate"
    # Responses from CalendarService to the request
    RESERVATION_IMPORT_CONFIRM = "reservation_import_confirm"
    RESERVATION_IMPORT_RESPONSE = "reservation_import_response"
    RESERVATION_IMPORT_OVERLAP = "reservation_import_overlap"
    # Responses from wrappers to the request
    RESERVATION_IMPORT = "reservation_import"
    # PropertyService to AnalyticsService
    GET_RECOMMENDED_PRICE = "get_recommended_price"
    SEND_DATA_TO_ANALYTICS = "send_data_to_analytics"
    # AnalyticsService to PropertyService
    RECOMMENDED_PRICE_RESPONSE = "recommended_price_response"
    RESERVATION_CANCEL_MESSAGE = "reservation_cancel_message"
    SCHEDULED_PROPERTY_IMPORT = "scheduled_property_import"
    RESERVATION_IMPORT_REQUEST_OTHER_SERVICES_CONFIRMED_RESERVATIONS = "reservation_import_request_other_services_confirmed_reservations"
    EMAIL_PROPERTY_ID_MAPPING = "mail_property_id_mapping"


class MessageFactory:
    @staticmethod
    def create_user_message(message_type: MessageType, user: BaseModel) -> BaseMessage:
        if message_type not in [
            MessageType.USER_CREATE,
            MessageType.USER_DELETE
        ]:
            raise ValueError("Invalid MessageType for User")
        return BaseMessage(message_type, user.model_dump(include={"email"}))

    @staticmethod
    def create_property(message_type: MessageType, prop: BaseModel) -> BaseMessage:
        # TODO change this function name
        if message_type == MessageType.PROPERTY_DELETE:
            return BaseMessage(message_type, prop.model_dump(include={"id"}))
        elif message_type == MessageType.PROPERTY_CREATE:
            return BaseMessage(message_type, prop.model_dump())
        raise ValueError("Invalid MessageType for Property")

    @staticmethod
    def create_property_update_message(internal_id: int, prop: dict) -> BaseMessage:
        return BaseMessage(MessageType.PROPERTY_UPDATE, {
            "internal_id": internal_id,
            "update_parameters": prop
        })

    @staticmethod
    def create_import_properties_message(user: BaseModel):
        return BaseMessage(MessageType.PROPERTY_IMPORT, user.model_dump(include={"email"}))

    @staticmethod
    def create_import_reservations_message(users):
        return BaseMessage(
            MessageType.RESERVATION_IMPORT_REQUEST,
            {"users_with_services": {user.email: [service.value for service in user.connected_services] for user in
                                     users}}
        )

    @staticmethod
    def create_reservation_import_initial_request_message(email: str, old_new_id_map: dict[int, int]):
        return BaseMessage(MessageType.RESERVATION_IMPORT_INITIAL_REQUEST, {
            "email": email,
            "old_new_id_map": old_new_id_map,
        })

    @staticmethod
    def create_import_properties_response_message(service: Service, properties: list):
        body = {
            "service": service.value,
            "properties": properties
        }
        return BaseMessage(MessageType.PROPERTY_IMPORT_RESPONSE, body)

    @staticmethod
    def create_import_reservations_response_message(service: Service, reservations: list):
        # TODO change import names in message type
        body = {
            "service": service.value,
            "reservations": reservations
        }
        return BaseMessage(MessageType.RESERVATION_IMPORT, body)

    @staticmethod
    def create_overlap_import_reservation_message(ex_reservation: dict):
        return BaseMessage(MessageType.RESERVATION_IMPORT_OVERLAP, {
            "old_reservation_internal_id": ex_reservation["_id"]
        })

    @staticmethod
    def create_confirm_reservation_message(ex_reservation: dict):
        return BaseMessage(MessageType.RESERVATION_IMPORT_CONFIRM, {
            "reservation_internal_id": ex_reservation["_id"],
            "property_internal_id": ex_reservation["property_id"],
            "begin_datetime": ex_reservation["begin_datetime"],
            "end_datetime": ex_reservation["end_datetime"],
        })

    @staticmethod
    def create_cancel_reservation_message(ex_reservation: dict):
        return BaseMessage(MessageType.RESERVATION_CANCEL_MESSAGE, {
            "old_reservation_internal_id": ex_reservation["_id"],
            "property_internal_id": ex_reservation["property_id"]
        })

    @staticmethod
    def create_get_recommended_price(properties: list):
        return BaseMessage(MessageType.GET_RECOMMENDED_PRICE, properties)

    @staticmethod
    def create_recommended_price_response_message(recommended_prices: dict):
        return BaseMessage(MessageType.RECOMMENDED_PRICE_RESPONSE, recommended_prices)
    
    @staticmethod
    def create_send_data_to_analytics_message(properties: list):
        return BaseMessage(MessageType.SEND_DATA_TO_ANALYTICS, properties)

    @staticmethod
    def create_management_event_creation_update_message(
            message_type: MessageType, property_internal_id: int, event_internal_id: int, begin_datetime: datetime,
            end_datetime: datetime
    ):
        if message_type not in [MessageType.MANAGEMENT_EVENT_CREATE, MessageType.MANAGEMENT_EVENT_UPDATE]:
            raise ValueError("Invalid MessageType for Management Event Message")

        return BaseMessage(message_type, {
            "property_internal_id": property_internal_id,
            "event_internal_id": event_internal_id,
            "begin_datetime": begin_datetime.strftime("%Y-%m-%dT%H:%M:%S"),
            "end_datetime": end_datetime.strftime("%Y-%m-%dT%H:%M:%S"),
        })

    @staticmethod
    def create_management_event_deletion_message(
            property_internal_id: int, event_internal_id: int
    ):
        message_body = {
            "property_internal_id": property_internal_id,
            "event_internal_id": event_internal_id
        }
        return BaseMessage(MessageType.MANAGEMENT_EVENT_DELETE, message_body)
    
    @staticmethod
    def create_scheduled_properties_import_message(users: list):
        return BaseMessage(
            MessageType.SCHEDULED_PROPERTY_IMPORT,
            {"users_with_services": {user.email: [service.value for service in user.connected_services] for user in
                                     users}}
        )

    @staticmethod
    def create_reservation_import_request_other_services_confirmed_reservations_message(service: Service, properties_ids: list):
        return BaseMessage(
            MessageType.RESERVATION_IMPORT_REQUEST_OTHER_SERVICES_CONFIRMED_RESERVATIONS,
            {
                "service": service.value,
                "properties_ids": properties_ids
            }
        )

    @staticmethod
    def create_email_property_id_mapping_message(email: str, property_id: int):
        return BaseMessage(
            MessageType.EMAIL_PROPERTY_ID_MAPPING, {"email": email, "property_id": property_id}
        )


def to_json(message: BaseMessage) -> str:
    return json.dumps(
        {"type": message.message_type, "ts": time(), "body": message.body}
    )


def from_json(json_str: str) -> BaseMessage:
    message = json.loads(json_str)
    return BaseMessage(message["type"], message["body"], message["ts"])


def to_json_aoi_bytes(message: BaseMessage) -> Message:
    return Message(body=json.dumps(
        {"type": message.message_type, "ts": time(), "body": message.body}
    ).encode())
