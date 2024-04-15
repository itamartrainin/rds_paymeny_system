#!/usr/bin/env python3

from simulator import Simulator

num_start_clients = 6
num_start_servers = 7
num_steps = 1000
num_total_tokens = 100
num_tokens_per_client = 10
max_messages_per_step = 5

sim = Simulator(num_start_clients, num_start_servers, num_total_tokens, num_tokens_per_client, max_messages_per_step)
for step in range(num_steps):
    print(f'--------- This is step: {step} ---------')
    sim.step()
