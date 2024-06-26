import uuid
from enum import Enum

import simulation_state

class AgentRole(Enum):
    CLIENT = 1
    SERVER = 2

class Token:
    def __init__(self):
        self.id = simulation_state.IDS.pop()
        self.version = 0
        self.owner = None

    @staticmethod
    def generate_id():
        return str(uuid.uuid4())

class ActionType(Enum):
    PAY_START = 1
    PAY_LINEARIZATION = 2
    PAY_FINISH = 3

    GET_TOKENS_START = 4
    GET_TOKENS_FINISH = 5

    CLIENT_TRANSFORM_START = 6
    CLIENT_TRANSFORM_FINISH = 7

    SERVER_TRANSFORM_START = 8
    SERVER_TRANSFORM_FINISH = 9

class MessageType(Enum):
    PAY = 1
    ACK_PAY = 2
    DB_UPDATE = 3
    GET_TOKENS = 4
    ACK_GET_TOKENS = 5
    ACK_DB_UPDATE = 6
    TURNED_TO_CLIENT = 7
    TURNED_TO_SERVER = 8

class Message:
    BROADCAST_ALL    = 0
    BROADCAST_SERVER = 1
    BROADCAST_CLIENT = 2

    def __init__(self, type : MessageType, sender_id, receiver_id, content):
        self.type = type
        self.sender_id = sender_id
        self.receiver_id = receiver_id
        self.content = content

    def __str__(self):
        return f"Type: {self.type}, From: {self.sender_id}, To: {self.receiver_id}, Content: {self.content}"