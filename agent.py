from abc import abstractmethod
from enum import Enum
import random
from typing import Optional
import uuid
from interfaces import AgentRole, Message, MessageType
import simulation_state

class Agent:
    def __init__(self, role : AgentRole, omission_rate = 0):
        self.omission_rate = float(omission_rate)
        self.transform_rate = 0.05
        self.tokens_db = None
        self.my_tokens = []
        self.role = role

        self.id = self.generate_id()

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

    def step(self, msg_in) -> Optional[Message]:
        def omission_msg(omission_rate = self.omission_rate):    
            # Drop messages according to the omission rate
            return random.random() < omission_rate
        
        msg_out = None

        # if received a message and it didn't omission - handle it according to the role
        if msg_in is not None and not omission_msg():
            msg_out = self.handle_incoming(msg_in)

        # If didn't receive a msg we can maybe transform or do a role action (only client)
        # Decide randomly if to transform
        elif self.should_transform():
            msg_out = self.transform()

        # Decide randomly if to do an action (clients only)
        elif self.role == AgentRole.CLIENT:
            msg_out = self.client_create_action()
        
        # Send output message if it didn't omission
        return msg_out if omission_msg() else None

    def handle_incoming(self, msg_in):
        if self.role == AgentRole.CLIENT:
            return self.client_handle_incoming(msg_in)
        elif self.role == AgentRole.SERVER:
            return self.server_handle_incoming(msg_in)

    def should_transform(self):
        # Check if can transform
        if (self.role == AgentRole.CLIENT and simulation_state.can_add_server()) or \
            (self.role == AgentRole.SERVER and simulation_state.can_remove_server()):
            # Randomly decide
            return random.random() < self.transform_rate

    def transform(self) -> Message:
        # Run the specific logic of the role
        if self.role == AgentRole.CLIENT:
            out_msg = self.client_transform()
        elif self.role == AgentRole.SERVER:
            out_msg = self.server_transform()

        # These actions should only happen after transform is finished
        # # Update the simulation state
        # simulation_state.update_lists(self)

        # # Change the role
        # self.role = AgentRole.SERVER if self.role == AgentRole.CLIENT else AgentRole.CLIENT

        return out_msg

    def decide_is_faulty(self):
        max_faulty = int(len(simulation_state.servers)/2)
        if len(simulation_state.faulty) < max_faulty:
            simulation_state.faulty.append(self.id)
            return True
        return False
    
    #################
    # Client Logics #
    #################

    def client_handle_incoming(self, msg_in):
        # Perform client/server logic based on incoming messages
        # Return new messages based on that logic.
        raise NotImplementedError('client message handling')
        
    def client_transform(self):
        raise NotImplementedError('client transforming')

    def client_create_action(self) -> Optional[Message]:
        ACTIONS = [[MessageType.PAY, MessageType.GET_TOKENS, None], 
                    [0.3,             0.4,                    0.3]]
    
        action_type = random.choices(ACTIONS[0], ACTIONS[1], k=1)[0]
        
        if action_type == MessageType.PAY and (len(self.my_tokens) > 0):
            return self.create_pay()
        elif action_type == MessageType.GET_TOKENS:
            return self.create_get_tokens()
        else:
            return None
        
    def create_pay(self) -> Message:
        # Choose a random token to send and a random owner to receive
        token_to_sell = random.choice(self.my_tokens)
        buyer_id = simulation_state.get_random_agent().id
        return Message(MessageType.PAY, self.id, Message.BROADCAST_SERVER, (token_to_sell.id, buyer_id, token_to_sell.version))

    def create_get_tokens(self) -> Message:
        # Choose a random owner to query about
        owner_id = simulation_state.get_random_agent().id
        return Message(MessageType.GET_TOKENS, self.id, Message.BROADCAST_SERVER, (owner_id))

    #################
    # Server Logics #
    #################

    def server_handle_incoming(self, msg_in):
        # Perform client/server logic based on incoming messages
        # Return new messages based on that logic.
        raise NotImplementedError('server message handling')
        
    def server_transform(self):
        raise NotImplementedError('server transforming')

    def server_handle_pay(self, msg : Message):
        raise NotImplementedError('server handle pay')
    
    def server_handle_get_tokens(self, msg : Message):
        raise NotImplementedError('server handle get tokens')