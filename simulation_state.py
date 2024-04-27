import random
import interfaces

# Configs
NUM_START_CLIENTS = 6
NUM_START_SERVERS = 7
NUM_TOKENS_PER_CLIENT = 10
MAX_MESSAGES_PER_STEP = 5
NUM_TOTAL_TOKENS = NUM_START_CLIENTS * NUM_TOKENS_PER_CLIENT

# ALLOW_FAULTY = True



# Rates
CLIENT_GET_RATE = 0     # 0 -> GET CANNOT HAPPEN RANDOMLY, ONLY AS PART OF PAY.
CLIENT_PAY_RATE = 0.3
CLIENT_NONE_RATE = 1 - CLIENT_PAY_RATE - CLIENT_GET_RATE

CLIENT_OMISSION_RATE = 0 # 0.3
SERVER_OMISSION_RATE = 0 # 0.8

CLIENT_TRANSFORM_RATE = 0.1 # 0.1
SERVER_TRANSFORM_RATE = 0 # 0.1


# Ongoing State
agents = {}
servers = {}
clients = {}
faulty_counter = 0 

def get_agents_amount():
    return len(agents.values())
def get_servers_amount():
    return len(servers.values())
def get_clients_amount():
    return len(clients.values())
def get_n_minus_t_amount():
    n = get_servers_amount()
    f = n // 2
    return n-f

def get_t_plus_one():
    n = get_servers_amount()
    f = n // 2
    return f+1

def get_agent_role_by_id(id):
    if id in servers:
        return interfaces.AgentRole.SERVER
    else:
        return interfaces.AgentRole.CLIENT

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