import copy
import random
from typing import List

import simulation_state
from interfaces import Message, Token

from agent import Agent

class Simulator:

    def __init__(self, num_start_clients, num_start_servers, total_tokens, num_tokens_per_client, max_messages_per_step):
        self.total_tokens = total_tokens
        self.num_tokens_per_client = num_tokens_per_client

        self.num_start_clients = num_start_clients
        self.num_start_servers = num_start_servers
        self.max_messages_per_step = max_messages_per_step

        self.tokens = {}
        self.agents = {}
        self.msgs_queue = []

        self.generate_tokens()
        self.init_agents()

        for agent in self.agents.values():
            agent.set_tokens_db(copy.deepcopy(self.tokens))

    def generate_tokens(self):
        self.tokens = {}
        for _ in range(self.total_tokens):
            t = Token()
            self.tokens[t.id] = t

    def init_agents(self):
        for i in range(self.num_start_clients + self.num_start_servers):
            is_server = (i >= self.num_start_clients)
            agent = Agent(is_server)

            if is_server:
                simulation_state.servers.append(agent.id)
            else:
                simulation_state.clients.append(agent.id)

            self.agents[agent.id] = agent

    def allocate_tokens(self, agent_id):
        allocated_tokens_counter = 0
        while allocated_tokens_counter < self.num_tokens_per_client:
            for token in list(self.tokens.values()):
                if token.owner is None:
                    token.owner = agent_id
                    allocated_tokens_counter += 1

    def step(self):
        # Randomly delay some of the messages to the next step
        to_deliver = self.choose_and_delay_messages()

        for msg in to_deliver:
            ret = self.agents[msg.receiver_id].step(msg)

            if ret is None:
                continue
        
            # If ret is a message, we need to append it to the queue.
            # If ret is a broadcast message, we need to duplicate the message to all servers
            if ret.get().receiver_id == Message.BROADCAST_SERVER:
                # Duplicate the message to all servers
                all_servers = simulation_state.get_all_servers()
                for server in all_servers:
                    duplicated_msg = ret.get().copy()
                    duplicated_msg.receiver_id = server.id
                    self.msgs_queue.append(duplicated_msg)
            else:
                self.msgs_queue.append(ret.get())

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
