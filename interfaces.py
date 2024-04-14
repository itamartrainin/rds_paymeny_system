import uuid

class Token:
    def __init__(self):
        self.id = self.generate_id()
        self.version = 0
        self.owner = None

    @staticmethod
    def generate_id():
        return str(uuid.uuid4())

class Message:
    def __init__(self, type, sender_id, receiver_id, content):
        self.type = type
        self.sender_id = sender_id
        self.receiver_id = receiver_id
        self.content = content