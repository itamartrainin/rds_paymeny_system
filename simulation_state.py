import random
import interfaces

agents = {}
servers = {}
clients = {}
faulty_counter = 0 

def get_random_server():
    # Choose a random server from the servers list
    return random.choice(list(servers.values()))
def get_random_client():
    # Choose a random client from the clients list
    return random.choice(list(clients.values()))
def get_random_agent():
    # Choose a random agent from the agents list
    return random.choice(list(agents.values()))

def get_all_servers():
    return servers.values()
def get_all_clients():
    return clients.values()
def get_all_agents():
    return agents.values()

def can_add_server():
    return len(servers.values()) < 7
def can_add_faulty_server():
    return (faulty_counter + 1) < len(servers.values()) / 2
def can_remove_server():
    return len(servers.values()) > 3

def update_lists(changed_agent):
    if changed_agent.role == interfaces.AgentRole.CLIENT:
        clients.pop(changed_agent.id)
        servers[changed_agent.id] = changed_agent
    elif changed_agent.role == interfaces.AgentRole.SERVER:
        servers.pop(changed_agent.id)
        clients[changed_agent.id] = changed_agent