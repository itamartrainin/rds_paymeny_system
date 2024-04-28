import copy
import random
from typing import List

import simulation_state
from interfaces import AgentRole, Message, Token

from agent import Agent

class Simulator:

    def __init__(self):
        self.tokens = {}
        simulation_state.agents = {}
        self.msgs_queue = []

        self.init_agents()
        self.generate_tokens()
        self.allocate_tokens()

        for agent in simulation_state.get_all_agents():
            agent.set_tokens_db(copy.deepcopy(self.tokens))

    def generate_tokens(self):
        self.tokens = {}
        for _ in range(simulation_state.NUM_TOTAL_TOKENS):
            t = Token()
            self.tokens[t.id] = t

    def init_agents(self):
        simulation_state.agents = {}
        simulation_state.servers = {}
        simulation_state.clients = {}

        for i in range(simulation_state.NUM_START_CLIENTS + simulation_state.NUM_START_SERVERS):
            if i >= simulation_state.NUM_START_CLIENTS:
                # Create SERVER
                agent_role = AgentRole.SERVER
                agent = Agent(agent_role)
                simulation_state.servers[agent.id] = agent
                # Make some servers faulty
                if simulation_state.ALLOW_FAULTY and simulation_state.faulty_counter < simulation_state.NUM_START_SERVERS / 2:
                    agent.set_omission_rate(simulation_state.SERVER_OMISSION_RATE)
                    agent.is_faulty = True
                    simulation_state.faulty_counter += 1
            else:
                # Create CLIENT
                agent_role = AgentRole.CLIENT
                agent = Agent(agent_role)
                simulation_state.clients[agent.id] = agent
                # if simulation_state.ALLOW_FAULTY and random.random() < simulation_state.CLIENT_FAULTY_RATE:
                #     agent.set_omission_rate(simulation_state.CLIENT_OMISSION_RATE)

            simulation_state.agents[agent.id] = agent

    def allocate_tokens(self):
        # Create a copy of the tokens list
        token_list_copy = copy.copy(list(self.tokens.values()))
        for client in simulation_state.get_all_clients():            
            # Randomly select 10 unique tokens for the client
            tokens_to_assign = random.sample(token_list_copy, simulation_state.NUM_TOKENS_PER_CLIENT)

            # Assign them to the client, removing from the list
            for token in tokens_to_assign:
                token.owner = client.id
                token_list_copy.remove(token)

    def step(self):
        # Randomly delay some of the messages to the next step
        to_deliver = self.choose_and_delay_messages()

        for msg in to_deliver:
            receiver_agent = simulation_state.agents[msg.receiver_id]

            print(f'===>RECEIVED<=== :: {msg.type} :: {simulation_state.get_agent_role_by_id(msg.sender_id)} [...{str(msg.sender_id)[-4:]}] --> {receiver_agent.role} [...{str(receiver_agent.id)[-4:]}]')
            response_msg = receiver_agent.step(msg)
            if response_msg is not None:
                print(f'<=====SENT=====> :: {response_msg.type} :: {receiver_agent.role} [...{str(receiver_agent.id)[-4:]}] --> {simulation_state.get_agent_role_by_id(response_msg.receiver_id)} [...{str(response_msg.receiver_id)[-4:]}]')
                self.add_msg_to_queue(response_msg)

        # No matter the messages, empty step all agents to generate actions
        for agent in simulation_state.get_all_agents():
            action_msg = agent.step(None)
            if action_msg is not None:
                print(f'<=====SENT=====> :: {action_msg.type} :: {agent.role} [...{str(agent.id)[-4:]}] --> [...{str(action_msg.receiver_id)[-4:]}]')
                self.add_msg_to_queue(action_msg)

    # Adds msg into the queue.
    # If the message is broadcast then we duplicate it for every server
    def add_msg_to_queue(self, msg):
        if msg.receiver_id == Message.BROADCAST_ALL:
            # Duplicate the message to all agents
            for agent in simulation_state.get_all_agents():
                duplicated_msg = copy.copy(msg)
                duplicated_msg.receiver_id = agent.id
                self.msgs_queue.append(duplicated_msg)
        elif msg.receiver_id == Message.BROADCAST_SERVER:
            # Duplicate the message to all servers
            for server in simulation_state.get_all_servers():
                duplicated_msg = copy.copy(msg)
                duplicated_msg.receiver_id = server.id
                self.msgs_queue.append(duplicated_msg)
        elif msg.receiver_id == Message.BROADCAST_CLIENT:
            # Duplicate the message to all clients
            for client in simulation_state.get_all_clients():
                duplicated_msg = copy.copy(msg)
                duplicated_msg.receiver_id = client.id
                self.msgs_queue.append(duplicated_msg)
        else:
            self.msgs_queue.append(msg)


    # Delays messages and returns ones to be sent in the current step
    def choose_and_delay_messages(self) -> List[Message]:
        to_deliver = []

        # Randomly shuffle the queue
        random.shuffle(self.msgs_queue)

        # Randomly select which messages to send in this step
        for msg in self.msgs_queue:
            if len(to_deliver) < simulation_state.MAX_MESSAGES_PER_STEP:
                self.msgs_queue.remove(msg)
                to_deliver.append(msg)

        return to_deliver

    def close(self):
        simulation_state.CLIENT_PAY_RATE = 0
        simulation_state.CLIENT_GET_RATE = 0
        simulation_state.CLIENT_NONE_RATE = 1
        simulation_state.CLIENT_TRANSFORM_RATE = 0
        simulation_state.SERVER_TRANSFORM_RATE = 0
