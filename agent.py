from abc import abstractmethod
from optparse import Option
import random
import uuid

from interfaces import Message
import simulation_state

class Agent:
    def __init__(self, is_server, omission_rate = 0):
        self.omission_rate = float(omission_rate)
        self.tokens_db = None
        self.my_tokens = [] 

        self.id = self.generate_id()

        # Importing Server and Client here avoids circular import
        from server import Server
        from client import Client
        self.role = Server if is_server else Client 

    def set_omission_rate(self, omission_rate):
        self.omission_rate = omission_rate

    @staticmethod
    def generate_id():
        owner_name = str(uuid.uuid4())
        simulation_state.owner_names.append(owner_name)
        return owner_name

    def set_tokens_db(self, tokens_db):
        self.tokens_db = tokens_db

        # Initialize my tokens from the whole dictionary
        for token in list(self.tokens_db.values()):
            if token.owner == self.id:
                self.my_tokens.append(token.id)

    def step(self, msg) -> Option[Message]:
        def omission_msg(self):    
            # Drop messages according to the omission rate
            return random.random() < self.omission_rate
        
        if omission_msg():
            return

        # 1. Handle incoming messages according to role
        outgoing_message = self.role.handle_incoming(msg)

        # 2. Transform
        if self.should_transform():
            self.transform()

        # 3. If client, do some action
        if not self.is_server:
            # If is client after transform, then can create pay messages
            # !Only after performing gettokens!
            # Some logic on generating pay messages
            pass

        return outgoing_message if omission_msg() else None

    @abstractmethod
    def handle_incoming(self, incoming_messages):
        # Perform client/server logic based on incoming messages
        # Return new messages based on that logic.
        pass

    def should_transform(self):
        # Decides weather should transform (randomly?) using simulation_state.num_servers, simulation_state.num_clients
        raise NotImplementedError('agent should transform')

    def transform(self):
        # Run the specific logic of the role
        self.role.transform()

        # Change the role
        self.role = Client if self.role == Server else Server

    def decide_is_faulty(self):
        max_faulty = int(len(simulation_state.servers)/2)
        if len(simulation_state.faulty) < max_faulty:
            simulation_state.faulty.append(self.id)
            return True
        return False
