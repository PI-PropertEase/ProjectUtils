import json
from enum import StrEnum
from time import time
from ProjectUtils.MessagingService.user_schemas import UserBase


class BaseType(StrEnum):
    pass


class BaseMessage:
    message_type = "BaseType"
    body = {}


class UserType(BaseType):
    CREATE_USER = "create_user"
    DELETE_USER = "delete_user"


class UserMessage(BaseMessage):
    def __init__(self, message_type: UserType, user: UserBase):
        self.message_type = message_type
        self.body = user.model_dump()


class PropertyType(BaseType):
    CREATE_PROPERTY = "new_property"
    UPDATE_PROPERTY = "update_property"
    DELETE_PROPERTY = "delete_property"


class PropertyMessage(BaseMessage):
    def __init__(self, message_type: PropertyType):
        self.message_type = message_type
        self.body = {}
        # TODO : continue body


def create_message(message: BaseMessage) -> str:
    return json.dumps({"type": message.message_type, "ts": time(), "body": message.body})


"""
Properties:
update_property_data
create_property
delete_property
"""
