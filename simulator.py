import copy
import random

import simulation_state
import interfaces

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
        self.active_messages = []

        self.generate_tokens()
        self.init_agents()

        for agent in self.agents.values():
            agent.set_tokens_db(copy.deepcopy(self.tokens))

    def generate_tokens(self):
        self.tokens = {}
        for _ in range(self.total_tokens):
            t = interfaces.Token()
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
        # 1. For each message in active_messages decide if delivers on this step (async delay)
        to_deliver, no_change = self.delay_messages()

        to_deliver_by_receiver = self.group_by_receiver(to_deliver)

        # 2. For each agent perform step and collect new messages. Take the agents randomly.
        new_msgs = []
        shuffled_agents = random.shuffle(self.agents.keys())
        for agent in shuffled_agents:
            ret = agent.step(to_deliver_by_receiver[agent.id])
            new_msgs.append(ret)

        self.active_messages = no_change + new_msgs

    def delay_messages(self):
        to_deliver = []
        no_change = []
        for msg in self.active_messages:
            if len(to_deliver) < self.max_messages_per_step and random.random() > 0.5:
                to_deliver.append(msg)
            else:
                no_change.append(msg)
        return to_deliver, no_change

    @staticmethod
    def group_by_receiver(to_deliver):
        to_deliver_by_receiver = {}
        for msg in to_deliver:
            if msg.receiver_id not in to_deliver_by_receiver:
                to_deliver_by_receiver[msg.receiver_id] = []
            to_deliver_by_receiver[msg.receiver_id].append(msg)
        return to_deliver_by_receiver
