from enum import StrEnum
from time import time
import json


class BaseType(StrEnum):
    pass


class BaseMessage:
    message_type = "BaseType"
    body = {}


class UserType(BaseType):
    CREATE_USER = "create_user"
    DELETE_USER = "delete_user"


class UserMessage(BaseMessage):
    def __init__(self, user_type: UserType, email: str):
        self.user_type = user_type
        self.body = {"email": email}


class PropertyType(BaseType):
    CREATE_PROPERTY = "new_property"
    UPDATE_PROPERTY = "update_property"
    DELETE_PROPERTY = "delete_property"


class PropertyMessage(BaseMessage):
    def __init__(self, property_type: PropertyType):
        self.property_type = property_type
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
