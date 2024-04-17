import copy
import random
from typing import List

import simulation_state
from interfaces import AgentRole, Message, Token

from agent import Agent

class Simulator:

    def __init__(self, num_start_clients, num_start_servers, total_tokens, num_tokens_per_client, max_messages_per_step):
        self.total_tokens = total_tokens
        self.num_tokens_per_client = num_tokens_per_client

        self.num_start_clients = num_start_clients
        self.num_start_servers = num_start_servers
        self.max_messages_per_step = max_messages_per_step

        self.tokens = {}
        simulation_state.agents = {}
        self.msgs_queue = []

        self.generate_tokens()
        self.init_agents()

        for agent in simulation_state.get_all_agents():
            agent.set_tokens_db(copy.deepcopy(self.tokens))

        self.allocate_tokens()

    def generate_tokens(self):
        self.tokens = {}
        for _ in range(self.total_tokens):
            t = Token()
            self.tokens[t.id] = t

    def init_agents(self):
        for i in range(self.num_start_clients + self.num_start_servers):
            if i >= self.num_start_clients:
                agent_role = AgentRole.SERVER
                agent = Agent(agent_role)
                simulation_state.servers[agent.id] = agent
                # Make some servers faulty
                if simulation_state.faulty_counter < self.num_start_servers / 2:
                    agent.set_omission_rate(0.8)
                    simulation_state.faulty_counter += 1
            else:
                agent_role = AgentRole.CLIENT
                agent = Agent(agent_role)
                simulation_state.clients[agent.id] = agent

            simulation_state.agents[agent.id] = agent

    def allocate_tokens(self):
        # Create a copy of the tokens list
        token_list_copy = copy.copy(list(self.tokens.values()))
        for client in simulation_state.get_all_clients():            
            # Randomly select 10 unique tokens for the client
            tokens_to_assign = random.sample(token_list_copy, self.num_tokens_per_client)

            # Assign them to the client, removing from the list
            for token in tokens_to_assign:
                token.owner = client.id
                client.my_tokens.append(token)
                token_list_copy.remove(token)

    def step(self):
        # Randomly delay some of the messages to the next step
        to_deliver = self.choose_and_delay_messages()

        for msg in to_deliver:
            response_msg = simulation_state.agents[msg.receiver_id].step(msg)
            self.add_msg_to_queue(response_msg) if response_msg is not None else None

        # No matter the messages, empty step all agents to generate actions
        for agent in simulation_state.get_all_agents():
            action_msg = agent.step(None)
            self.add_msg_to_queue(action_msg) if action_msg is not None else None

    # Adds msg into the queue.
    # If the message is broadcast then we duplicate it for every server
    def add_msg_to_queue(self, msg):
        if msg.receiver_id == Message.BROADCAST_SERVER:
            # Duplicate the message to all servers
            for server in simulation_state.get_all_servers():
                duplicated_msg = copy.copy(msg)
                duplicated_msg.receiver_id = server.id
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
            if len(to_deliver) < self.max_messages_per_step and random.random() > 0.5:
                self.msgs_queue.remove(msg)
                to_deliver.append(msg)

        return to_deliver
