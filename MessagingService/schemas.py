import json
from enum import StrEnum
from time import time
from pydantic import BaseModel
from typing import Union, Dict, List
from aio_pika import Message


class BaseMessage:
    def __init__(self, message_type: str, body: Union[Dict, List], ts: float = None):
        self.message_type = message_type
        self.body = body
        self.ts = ts if ts is not None else time()


class MessageType(StrEnum):
    USER_CREATE = "user_create"
    USER_DELETE = "user_delete"
    PROPERTY_IMPORT = "property_import"
    PROPERTY_IMPORT_RESPONSE = "property_import_response"
    PROPERTY_IMPORT_DUPLICATE = "property_import_duplicate"
    PROPERTY_CREATE = "property_create"
    PROPERTY_UPDATE = "property_update"
    PROPERTY_DELETE = "property_delete"
    RESERVATION_CREATE = "reservation_create"
    RESERVATION_UPDATE = "reservation_update"
    RESERVATION_DELETE = "reservation_delete"


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
        if message_type == MessageType.PROPERTY_DELETE:
            return BaseMessage(message_type, prop.model_dump(include={"id"}))
        elif message_type in [
            MessageType.PROPERTY_CREATE,
            MessageType.PROPERTY_UPDATE
        ]:
            return BaseMessage(message_type, prop.model_dump())
        raise ValueError("Invalid MessageType for Property")

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
    def create_duplicate_import_property_message(ex_prop: dict, ps_prop: dict):
        return BaseMessage(MessageType.PROPERTY_IMPORT_DUPLICATE, {
            "old_internal_id": ex_prop["_id"],
            "new_internal_id": ps_prop["_id"]
        })

    @staticmethod
    def create_import_properties_response_message(properties: list):
        return BaseMessage(MessageType.PROPERTY_IMPORT_RESPONSE, properties)


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
