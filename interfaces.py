import uuid

class Token:
    def __init__(self):
        self.id = self.generate_id()
        self.version = 0
        self.owner = None

    @staticmethod
    def generate_id():
        return str(uuid.uuid4())
