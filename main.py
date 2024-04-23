#!/usr/bin/env python3

from interfaces import MessageType
from simulator import Simulator
import simulation_state

num_start_clients = 6
num_start_servers = 7
num_steps = 100
num_tokens_per_client = 10
max_messages_per_step = 5

num_total_tokens = num_start_clients * num_tokens_per_client
sim = Simulator(num_start_clients, num_start_servers, num_total_tokens, num_tokens_per_client, max_messages_per_step)

print("Start:")
for agent in simulation_state.get_all_agents():
    print(f"Agent: {agent.id}")
    print(f"Tokens: {agent.my_tokens}")

# Example for register_upon usage:
# simulation_state.get_random_server().register_upon(lambda agent, msgs: print("Success!"), 
#                                                     lambda msg: msg.type == MessageType.GET_TOKENS, 3)

for step in range(num_steps):
    print(f'--------- This is step: {step} ---------')
    print('\n'.join(str(msg) for msg in sim.msgs_queue))
    sim.step()

print("Summary:")
for agent in simulation_state.get_all_agents():
    print(f"Agent: {agent.id}")
    print(f"Tokens: {agent.my_tokens}")


