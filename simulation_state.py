import random

agents = []
servers = []
clients = []
faulty = []

def get_random_server():
    # Choose a random server from the servers list
    return random.choice(servers)

def get_random_client():
    # Choose a random client from the clients list
    return random.choice(clients)

def get_random_agent():
    # Choose a random agent from the agents list
    return random.choice(agents)

def get_all_servers():
    return servers

def get_all_clients():
    return clients

def get_all_agents():
    return agents