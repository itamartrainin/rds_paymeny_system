from simulator import Simulator

num_start_clients = 6
num_start_servers = 7
num_steps = 1000
num_total_tokens = 100
num_tokens_per_client = 10

sim = Simulator(num_start_clients, num_start_servers, num_total_tokens, num_tokens_per_client)
for step in range(num_steps):
    print(f'--------- This is step: {step} ---------')
    sim.step()
