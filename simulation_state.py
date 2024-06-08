import random
import interfaces

# Configs

# Simulations
NUM_SIMULATIONS = 10
STEPS_UNTIL_CLOSE = 200
STEPS_UNTIL_INFTY_LOOP = 10000 * STEPS_UNTIL_CLOSE

# Servers and Client amounts
MIN_SERVERS = 3
MAX_SERVERS = 7
NUM_START_CLIENTS = 6
NUM_START_SERVERS = 7

# Tokens
NUM_TOKENS_PER_CLIENT = 10
NUM_TOTAL_TOKENS = NUM_START_CLIENTS * NUM_TOKENS_PER_CLIENT

# Messages
MAX_MESSAGES_PER_STEP = 5
ACTION_TIMEOUT = 30

# ALLOW_FAULTY = True

# Rates
CLIENT_GET_RATE = 0     # 0 -> GET CANNOT HAPPEN RANDOMLY, ONLY AS PART OF PAY.
CLIENT_PAY_RATE = 0.3
CLIENT_NONE_RATE = 1 - CLIENT_PAY_RATE - CLIENT_GET_RATE

CLIENT_OMISSION_RATE = 0 # 0.3
SERVER_OMISSION_RATE = 0 # 0.8

CLIENT_TRANSFORM_RATE = 0.1 # 0.1
SERVER_TRANSFORM_RATE = 0.1 # 0.1

IDS = None

# Ongoing State
agents = {}
servers = {}
server_transforming_flag = 0 # We allow only one server to transform at a time
clients = {}
client_transforming_flag = 0 # We allow only one client to transform at a time
amount_transforming_into_clients = 0
faulty_counter = 0 
step_counter = 0

# Logs
LOG_RUN = 0
READ_FROM_LOG = LOG_RUN
WRITE_TO_LOG = 1 - READ_FROM_LOG

if LOG_RUN:
    LOG_POP_RATE = 0.5

action_log = [] # list of actions tuple : (agent_id, step, action)

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
    return len(servers.values()) - server_transforming_flag + client_transforming_flag < MAX_SERVERS
def can_remove_server():
    return len(servers.values()) - server_transforming_flag + client_transforming_flag > MIN_SERVERS
def can_add_faulty_server():
    return (faulty_counter + 1) < len(servers.values()) / 2

def update_lists(changed_agent):
    if changed_agent.role == interfaces.AgentRole.CLIENT:
        clients.pop(changed_agent.id)
        servers[changed_agent.id] = changed_agent
    elif changed_agent.role == interfaces.AgentRole.SERVER:
        servers.pop(changed_agent.id)
        clients[changed_agent.id] = changed_agent


# Helper functions for calculating linearizability of PAY actions
ongoing_pay_actions = {}

def mark_pay_start(agent_id, step):
    ongoing_pay_actions[agent_id] = [step, 0]

def mark_pay_answer(agent_id, step):
    # If the agent is not in the ongoing pay actions, ignore the message
    if agent_id not in ongoing_pay_actions:
        return

    ongoing_pay_actions[agent_id][1] += 1

    # Check if enough servers answered - meaning this is the linearization point
    if ongoing_pay_actions[agent_id][1] == get_n_minus_t_amount():
        ongoing_pay_actions.pop(agent_id)
        
        # Log the linearization point
        agents[agent_id].log_action(interfaces.ActionType.PAY_LINEARIZATION)
