from agent import Agent
from interfaces import Message

class Server(Agent):
    def __init__(self):
        pass

    def handle_incoming(self : Agent, msg_in):
        # Perform client/server logic based on incoming messages
        # Return new messages based on that logic.
        raise NotImplementedError('server message handling')
        
    def transform(self : Agent):
        raise NotImplementedError('server transforming')

    def handle_pay(self : Agent, msg : Message):
        raise NotImplementedError('server handle pay')
    
    def handle_get_tokens(self : Agent, msg : Message):
        raise NotImplementedError('server handle get tokens')