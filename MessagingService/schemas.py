import json
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
    RESERVATION_CREATE = "reservation_create"
    RESERVATION_UPDATE = "reservation_update"
    RESERVATION_DELETE = "reservation_delete"
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
    # PropertyService to AnalyticsService
    GET_RECOMMENDED_PRICE = "get_recommended_price"
    # AnalyticsService to PropertyService
    RECOMMENDED_PRICE_RESPONSE = "recommended_price_response"


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
    def create_reservation_message(message_type: MessageType, reservation: BaseModel) -> BaseMessage:
        if message_type == MessageType.RESERVATION_DELETE:
            return BaseMessage(message_type, reservation.model_dump(include={"id"}))
        elif message_type in [
            MessageType.RESERVATION_CREATE,
            MessageType.RESERVATION_UPDATE,
        ]:
            return BaseMessage(message_type, reservation.model_dump())
        raise ValueError("Invalid MessageType for Reservation")

    @staticmethod
    def create_import_properties_message(user: BaseModel):
        return BaseMessage(MessageType.PROPERTY_IMPORT, user.model_dump(include={"email"}))

    @staticmethod
    def create_import_reservations_message(users):
        return BaseMessage(
            MessageType.RESERVATION_IMPORT_REQUEST,
            {"users_with_services": { user.email: [service.value for service in user.connected_services] for user in users}}
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
            "old_internal_id": ex_reservation["_id"]
        })

    @staticmethod
    def create_confirm_reservation_message(ex_reservation: dict):
        return BaseMessage(MessageType.RESERVATION_IMPORT_CONFIRM, {
            "internal_id": ex_reservation["_id"]
        })
    
    @staticmethod
    def create_get_recommended_price(properties: list):
        return BaseMessage(MessageType.GET_RECOMMENDED_PRICE, properties)

    @staticmethod
    def create_recommended_price_response_message(recommended_prices: dict):
        return BaseMessage(MessageType.RECOMMENDED_PRICE_RESPONSE, recommended_prices)

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
