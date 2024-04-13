from simulator import Simulator

num_start_clients = 6
num_start_servers = 7
num_steps = 1000

sim = Simulator(num_start_clients, num_start_servers)
for step in range(num_steps):
    print(f'--------- This is step: {step} ---------')
    sim.step()
