from abc import abstractmethod
import random
from typing import Optional
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

        # Add self to the global list
        simulation_state.agents.append(self)
        simulation_state.servers.append(self) if is_server else simulation_state.clients.append(self)


    def set_omission_rate(self, omission_rate):
        self.omission_rate = omission_rate

    @staticmethod
    def generate_id():
        owner_name = str(uuid.uuid4())
        return owner_name

    def set_tokens_db(self, tokens_db):
        self.tokens_db = tokens_db

        # Initialize my tokens from the whole dictionary
        for token in list(self.tokens_db.values()):
            if token.owner == self.id:
                self.my_tokens.append(token.id)

    def step(self, msg) -> Optional[Message]:
        def omission_msg(self):    
            # Drop messages according to the omission rate
            return random.random() < self.omission_rate
        
        # if received a message and it didn't omission - handle it according to the role
        if msg is not None and not omission_msg():
            outgoing_message = self.role.handle_incoming(msg)    

        # Decide randomly if to transform
        if self.should_transform():
            self.transform()

        # Decide randomly if to do an action (clients only)
        if self.role == Client:
            print ("action")
            self.role.create_action()
            pass
        
        # Send output message if it didn't omission
        return outgoing_message if omission_msg() else None

    @abstractmethod
    def handle_incoming(self, msg_in):
        # Perform client/server logic based on incoming messages
        # Return new messages based on that logic.
        pass

    def should_transform(self):
        # Decides weather should transform (randomly?) using simulation_state.num_servers, simulation_state.num_clients
        raise NotImplementedError('agent should transform')

    def transform(self):
        # Run the specific logic of the role
        self.role.transform()

        # Change the role and update the simulation state
        if self.role == Server:
            self.role = Client
            simulation_state.servers.remove(self)
            simulation_state.clients.append(self)
        elif self.role == Client:
            self.role = Server
            simulation_state.clients.remove(self)
            simulation_state.servers.append(self)

    def decide_is_faulty(self):
        max_faulty = int(len(simulation_state.servers)/2)
        if len(simulation_state.faulty) < max_faulty:
            simulation_state.faulty.append(self.id)
            return True
        return False
