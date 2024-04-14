import simulation_state
import interfaces
import uuid

from agent import Agent

class Simulator:

    def __init__(self, num_start_clients, num_start_servers, total_tokens, num_tokens_per_client):
        self.total_tokens = total_tokens
        self.num_tokens_per_client = num_tokens_per_client

        simulation_state.num_clients = num_start_clients
        simulation_state.num_servers = num_start_servers

        self.tokens = []
        self.agents = []
        self.active_messages = []

        self.generate_tokens()
        self.init_agents()

    def generate_tokens(self):
        self.tokens = {}
        for _ in range(self.total_tokens):
            t = interfaces.Token()
            self.tokens[t.id] = t

    def init_agents(self):
        for i in range(simulation_state.num_clients + simulation_state.num_servers):
            if i < simulation_state.num_clients:
                is_server = (i >= simulation_state.num_clients)
                tokens = self.tokens[i*self.num_tokens_per_client:(i+1)*self.num_tokens_per_client]
                Agent(is_server, tokens)

    def step(self):
        """
        1. For each message in active_messages decide if delivers on this step (async delay)
        2. For each agnet perform setep and collect new messages
        3. For each client message print performed actions
        """