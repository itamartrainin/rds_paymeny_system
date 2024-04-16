import random
from typing import Optional
from agent import Agent
from interfaces import Message, MessageType
from simulation_state import get_random_agent

class Client(Agent):
    ACTIONS = [[MessageType.PAY, MessageType.GET_TOKENS, None], 
               [0.3,             0.4,                    0.3]]
    
    def __init__(self):
        pass

    def handle_incoming(self : Agent, msg_in):
        # Perform client/server logic based on incoming messages
        # Return new messages based on that logic.
        raise NotImplementedError('client message handling')
        
    def transform(self : Agent):
        raise NotImplementedError('client transforming')

    def create_action(self) -> Optional[Message]:
        action_type = random.choices(self.ACTIONS[0], self.ACTIONS[1], k=1)[0]
        
        if action_type == MessageType.PAY:
            return self.create_pay()
        elif action_type == MessageType.GET_TOKENS:
            return self.create_get_tokens()
        else:
            return None

    def create_pay(self) -> Message:
        # Choose a random token to send and a random owner to receive
        token_to_sell = random.choices(self.my_tokens)
        buyer_id = get_random_agent().id
        return Message(MessageType.PAY, self.id, Message.BROADCAST_SERVER, (token_to_sell.id, buyer_id, token_to_sell.version))

    def create_get_tokens(self) -> Message:
        # Choose a random owner to query about
        owner_id = get_random_agent().id
        return Message(MessageType.GET_TOKENS, self.id, Message.BROADCAST_SERVER, (owner_id))
