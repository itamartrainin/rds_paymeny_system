from abc import abstractmethod
import copy
from enum import Enum
import random
from typing import List, Optional
import uuid
from interfaces import AgentRole, Message, MessageType, Token
import simulation_state

class Agent:
    def __init__(self, role: AgentRole, omission_rate=0):
        self.omission_rate = float(omission_rate)
        self.tokens_db = None
        self.my_tokens = []
        self.role = role
        self.upon_registry = []
        self.id = self.generate_id()
        self.during_action = False
        self.is_faulty = False

    def set_omission_rate(self, omission_rate):
        self.omission_rate = omission_rate
        # if is server and omission rate is positive, this is faulty
        if omission_rate > 0:
            self.is_faulty = True

    @staticmethod
    def generate_id():
        owner_name = str(uuid.uuid4())
        return owner_name

    def set_tokens_db(self, tokens_db):
        self.tokens_db = tokens_db

        # Initialize my tokens from the whole dictionary
        for token in list(self.tokens_db.values()):
            if token.owner == self.id:
                self.my_tokens.append(token)

    def step(self, msg_in) -> Optional[Message]:
        def omit_msg(omission_rate = self.omission_rate):
            # Drop messages according to the omission rate
            return self.is_faulty and (random.random() < omission_rate)

        msg_out = None

        # if received a message and it didn't omission - handle it according to the role
        should_omit_incoming = omit_msg()
        if msg_in is not None and not should_omit_incoming:
            # Agent decided not to omit incoming message.
            msg_out = self.handle_incoming(msg_in)

        # For simplicity, we ignore sending omission when running a self initiated action
        # If didn't receive a msg we can maybe do an action (if one is not in progress)
        # Decide randomly if to transform
        elif not self.during_action and self.should_transform():
            msg_out = self.transform()
            self.last_action_msg = msg_out

        # Decide randomly if to do an action (clients only)
        elif not self.during_action and self.role == AgentRole.CLIENT:
            msg_out = self.client_create_action()
            self.last_action_msg = msg_out

        #TODO: only drop regular responses and not actions
        should_omit_outgoing = omit_msg()
        if should_omit_outgoing:
            # Agent decides to omit outgoing message
            msg_out = None

        return msg_out

    def handle_incoming(self, msg_in):
        # Check if we are waiting for this type of message:
        for upon in self.upon_registry:
            func_to_run, upon_filter, upon_amount, msgs = upon
            if upon_filter(msg_in):
                msgs.append(msg_in)
                
                # If enough messages where received run the function and remove the upon
                if len(msgs) >= upon_amount():
                    self.upon_registry.remove(upon)
                    msg = func_to_run(self, msgs)
                    return msg

        # Messages we didn't specifically wait for
        if self.role == AgentRole.CLIENT:
            return self.client_handle_incoming(msg_in)
        elif self.role == AgentRole.SERVER:
            return self.server_handle_incoming(msg_in)

    def should_transform(self):
        # Check if can transform
        if (self.role == AgentRole.CLIENT and simulation_state.can_add_server()) or \
            (self.role == AgentRole.SERVER and simulation_state.can_remove_server()):
            # Randomly decide
            rand_choice = random.random()
            if self.role == AgentRole.CLIENT:
                return rand_choice < simulation_state.CLIENT_TRANSFORM_RATE and not simulation_state.client_transforming_flag
            elif self.role == AgentRole.SERVER:
                return rand_choice < simulation_state.SERVER_TRANSFORM_RATE and not simulation_state.server_transforming_flag
        return False

    def transform(self) -> Message:
        
        # Run the specific logic of the role
        if self.role == AgentRole.CLIENT:
            simulation_state.client_transforming_flag = 1
            out_msg = self.transform_to_server()
        elif self.role == AgentRole.SERVER:
            simulation_state.server_transforming_flag = 1
            out_msg = self.transform_to_client()

        return out_msg or None

    # Register a function to run when receiving an amount of messages of the same type
    def register_upon(self, func_to_run, upon_filter, upon_amount):
        self.upon_registry.append((func_to_run, upon_filter, upon_amount, []))    

    def give_token(self, token: Token):
        self.my_tokens.append(token)

    def remove_token(self, token: Token):
        self.my_tokens.remove(token)
    
    #################
    # Client Logics #
    #################

    def client_handle_incoming(self, msg_in):
        # Client can only handle incoming TURNED_TO_CLIENT messages, which trigger a recount of upons
        if msg_in.type == MessageType.TURNED_TO_CLIENT:
            for upon in self.upon_registry:
                func_to_run, _, upon_amount, msgs = upon
                if len(msgs) >= upon_amount():
                    self.upon_registry.remove(upon)
                    return func_to_run(self, msgs)
        
        # if a client turned server, we send him our in-process action
        if msg_in.type == MessageType.TURNED_TO_SERVER and self.during_action:
            copy_last_action = copy.deepcopy(self.last_action_msg) 
            copy_last_action.receiver_id = msg_in.sender_id
            return copy_last_action

        return None
        
    def transform_to_server(self):
        print(f'!TRANSFORMATION! :: [...{str(self.id)[-4:]}] :: ~INITIATED~ :: CLIENT --> SERVER.')
        # Agent sends a getToken request to update the db, and upon finishing the agent transforms

        # send <getToken, > to all
        owner_id = ""
        to_send = Message(MessageType.GET_TOKENS, self.id, Message.BROADCAST_SERVER, ())

        # When receiving answers
        def handle_transform_get(agent : Agent, msgs : List[Message]):
            # Reset the inner db
            agent.tokens_db = {}
            for msg in msgs:
                tokens_list = msg.content
                for token in tokens_list:
                    # If we already have this token, update it if the version is higher
                    if token.id in agent.tokens_db:
                        if token.version > agent.tokens_db[token.id].version:
                            agent.tokens_db[token.id] = token
                    else:
                        agent.tokens_db[token.id] = token

            # Unlock action-doing
            agent.during_action = False

            # Turn into a server
            del simulation_state.clients[self.id]
            simulation_state.servers[self.id] = self
            self.role = AgentRole.SERVER
            simulation_state.client_transforming_flag = 0

            print(f'!TRANSFORMATION! :: [...{str(self.id)[-4:]}] :: ~DONE~ :: CLIENT --> SERVER.')

            if simulation_state.ALLOW_FAULTY and simulation_state.faulty_counter < len(simulation_state.servers)/2:
                self.set_omission_rate(simulation_state.FAULTY_OMISSION_RATE)
                simulation_state.faulty_counter += 1

            # Tell clients to send their actions
            return Message(MessageType.TURNED_TO_SERVER, agent.id, Message.BROADCAST_CLIENT, ())

        # Register the function to handle the incoming messages
        self.register_upon(handle_transform_get, 
                        lambda msg: msg.type == MessageType.ACK_GET_TOKENS, simulation_state.get_n_minus_t_amount)
        
        # Lock action-doing
        self.during_action = True

        return to_send

    def client_create_action(self) -> Optional[Message]:
        ACTIONS = [
            [MessageType.PAY, MessageType.GET_TOKENS, None], 
            [simulation_state.CLIENT_PAY_RATE, simulation_state.CLIENT_GET_RATE, simulation_state.CLIENT_NONE_RATE]
        ]
    
        action_type = random.choices(ACTIONS[0], ACTIONS[1], k=1)[0]
        
        if action_type == MessageType.PAY and (len(self.my_tokens) > 0):
            return self.run_get_then_pay_request()
        elif action_type == MessageType.GET_TOKENS:
            return self.run_get_request()
        else:
            return None

    def run_get_then_pay_request(self):
        return self.run_get_request(part_of_pay_request=True)

    def run_pay_request(self) -> Message:
        # Choose a random token to send and a random owner to receive

        token_to_sell = random.choice(self.my_tokens)
        buyer_id = simulation_state.get_random_agent().id
        to_send = Message(MessageType.PAY, self.id, Message.BROADCAST_SERVER, (token_to_sell.id, buyer_id, token_to_sell.version + 1))

        print(f'~~PAY//STARTED~~ :: [...{str(self.id)[-4:]}]')
        print(f'$$$TOKEN-SUGG$$$ :: Token ID: [...{str(token_to_sell.id)[-4:]}] / Version: {token_to_sell.version} :: [...{str(self.id)[-4:]}] --> [...{str(buyer_id)[-4:]}]')

        # When receiving answers, remove the sold token from the list
        def handle_ack_pay(agent : Agent, msgs : List[Message]):
            print(f'~~~PAY//ENDED~~~ :: [...{str(agent.id)[-4:]}]')
            print(f'$$$TOKEN-SOLD$$$ :: Token ID: [...{str(token_to_sell.id)[-4:]}] / Version: {token_to_sell.version} :: [...{str(self.id)[-4:]}] --> [...{str(buyer_id)[-4:]}]')

            # Update the version of the token then do the transfer
            token_to_sell.version += 1 
            self.my_tokens.remove(token_to_sell)
            simulation_state.agents[buyer_id].my_tokens.append(token_to_sell)

            # Unlock action-doing
            agent.during_action = False

        # Wait for ACK_PAY responses with the right token_id and version
        def handle_ack_filter(msg : Message) -> bool:
            if msg.type != MessageType.ACK_PAY:
                return False
            
            token_id, token_version = msg.content
            return token_id == token_to_sell.id and token_version == (token_to_sell.version + 1)

        # Register the handling
        self.register_upon(handle_ack_pay, handle_ack_filter, simulation_state.get_n_minus_t_amount)
        
        # Lock action-doing
        self.during_action = True

        return to_send

    def run_get_request(self, part_of_pay_request=False) -> Message:
        # send <getToken, random_owner> to all

        owner_id = simulation_state.get_random_agent().id
        to_send = Message(MessageType.GET_TOKENS, self.id, Message.BROADCAST_SERVER, ())

        # When receiving answers
        def handle_ack_tokens(agent : Agent, msgs : List[Message]):
            print(f'~~~GET//ENDED~~~ :: [...{str(agent.id)[-4:]}]')

            # Reset the inner db
            agent.tokens_db = {}
            for msg in msgs:
                tokens_list = msg.content
                for token in tokens_list:
                    # If we already have this token, update it if the version is higher
                    if token.id in agent.tokens_db:
                        if token.version > agent.tokens_db[token.id].version:
                            agent.tokens_db[token.id] = token
                    else:
                        agent.tokens_db[token.id] = token

            # Filter tokens by owner_id
            owner_tokens = [(token_id, token) for token_id, token in agent.tokens_db.items() if token.owner == owner_id]
            # Now the db is updated and owner_tokens holds all tokens belonging to the requested owner - what are we supposed to do?
            # TODO: understand this
            # print("Managed to collect get for " + owner_id)
            # print(owner_tokens)

            if part_of_pay_request:
                msg_out = self.run_pay_request()
                self.last_action_msg = msg_out

            # Unlock action-doing
            agent.during_action = False

            return None

        # Register the function to handle the incoming messages
        self.register_upon(handle_ack_tokens, 
                        lambda msg: msg.type == MessageType.ACK_GET_TOKENS, simulation_state.get_n_minus_t_amount)
        
        # Lock action-doing
        self.during_action = True

        return to_send

    #################
    # Server Logics #
    #################

    def server_handle_incoming(self, msg_in: Message):
        if msg_in.type == MessageType.PAY:
            return self.server_handle_pay(msg_in)
        elif msg_in.type == MessageType.GET_TOKENS:
            return self.server_handle_get_tokens(msg_in)
        elif msg_in.type == MessageType.DB_UPDATE:
            return self.server_handle_db_update(msg_in)

    def server_handle_pay(self, msg_in: Message):
        # Message looks like this: <pay, token_id, new_owner, new_version>
        token_id, new_owner, new_version = msg_in.content
        token = self.tokens_db[token_id]

        # Check that this version is newer - won't happen only if this is an old message
        if token is not None and token.version <= new_version:
            # Transfer token to buyer
            token.owner = new_owner
            token.version = new_version
            return Message(MessageType.ACK_PAY, self.id, msg_in.sender_id, (token_id, token.version))

    def server_handle_get_tokens(self, msg_in: Message):
        # Send all of the tokens as a list
        return Message(MessageType.ACK_GET_TOKENS, self.id, msg_in.sender_id, (list(self.tokens_db.values())))

    def server_handle_db_update(self, msg_in: Message):
        # Update local DB based on version then ACK back.
        tokens_list = msg_in.content
        for token in tokens_list:
            # If we already have this token, update it if the version is higher
            if token.id in self.tokens_db:
                if token.version > self.tokens_db[token.id].version:
                    self.tokens_db[token.id] = token
            else:
                self.tokens_db[token.id] = token

        return Message(MessageType.ACK_DB_UPDATE, self.id, msg_in.sender_id, ())

    def transform_to_client(self):
        print(f'!TRANSFORMATION! :: [...{str(self.id)[-4:]}] :: ~INITIATED~ :: SERVER --> CLIENT.')
        to_send = self.run_db_update_request()
        return to_send

    def run_db_update_request(self) -> Message:
        # Send my db to all others and ask them to update their own based on my db
        # send <dbUpdate, my_db> to all

        to_send = Message(MessageType.DB_UPDATE, self.id, Message.BROADCAST_SERVER, (list(self.tokens_db.values())))

        # When receiving answers
        def handle_ack_db_update(agent: Agent, msgs: List[Message]):
            # Actual transformation to client logic
            # Transform only if there are less faulty servers than required or self is a faulty server
            if agent.is_faulty or simulation_state.faulty_counter < (len(simulation_state.servers) - 1) / 2:
                del simulation_state.servers[agent.id]
                simulation_state.clients[agent.id] = agent
                agent.role = AgentRole.CLIENT
                simulation_state.server_transforming_flag = 0

                # Decide if new client is faulty
                # if simulation_state.ALLOW_FAULTY and random.random() < simulation_state.CLIENT_FAULTY_RATE:
                #     agent.set_omission_rate(simulation_state.CLIENT_OMISSION_RATE)

                if self.is_faulty:
                    agent.set_omission_rate(simulation_state.CLIENT_OMISSION_RATE)

                print(f'!TRANSFORMATION! :: [...{str(agent.id)[-4:]}] :: ~DONE~ :: SERVER --> CLIENT.')

                # Unlock action-doing
                agent.during_action = False

                # Send a message to all clients to announce change
                return Message(MessageType.TURNED_TO_CLIENT, agent.id, Message.BROADCAST_CLIENT, ())

        # Register the function to handle the incoming messages
        self.register_upon(handle_ack_db_update,
                           lambda msg: msg.type == MessageType.ACK_DB_UPDATE, simulation_state.get_t_plus_one)

        # Lock action-doing
        self.during_action = True

        return to_send