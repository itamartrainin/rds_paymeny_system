import uuid
from enum import Enum

class AgentRole(Enum):
    CLIENT = 1
    SERVER = 2

class Token:
    def __init__(self):
        self.id = self.generate_id()
        self.version = 0
        self.owner = None

    @staticmethod
    def generate_id():
        return str(uuid.uuid4())

class MessageType(Enum):
    PAY = 1
    ACK_PAY = 2
    GET_TOKENS = 3
    ACK_GET_TOKENS = 4
    OK = 5

class Message:
    BROADCAST_SERVER = 1

    def __init__(self, type : MessageType, sender_id, receiver_id, content):
        self.type = type
        self.sender_id = sender_id
        self.receiver_id = receiver_id
        self.content = content

    def __str__(self):
        return f"Type: {self.type}, From: {self.sender_id}, To: {self.receiver_id}, Content: {self.content}"