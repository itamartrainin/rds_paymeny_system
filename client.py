from typing import Optional
from agent import Agent
from interfaces import Message

class Client(Agent):
    def __init__(self):
        pass

    def handle_incoming(self : Agent, incoming_messages):
        # Perform client/server logic based on incoming messages
        # Return new messages based on that logic.
        raise NotImplementedError('client message handling')
        
    def transform(self : Agent):
        raise NotImplementedError('client transforming')

    def create_action(self) -> Optional[Message]:
        # Randomly choose whether to create pay or get token or none and return it 
        pass

    def create_pay(self : Agent) -> Message:
        # Choose a random token to send
        # Choose a random owner to send the token to
        # Create a pay message
        raise NotImplementedError('client create pay')
    
    def create_get_tokens(self : Agent) -> Message:
        # Choose a random owner to query about 
        # Create a get_tokens message
        raise NotImplementedError('client create get tokens')
