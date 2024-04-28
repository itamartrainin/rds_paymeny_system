#!/usr/bin/env python3

from interfaces import AgentRole, MessageType
from simulator import Simulator
import simulation_state


def run_simulation_test():
    sim = Simulator()

    # Print starting state
    print("Start:")
    print_summary()

    # Run steps until close
    for step in range(STEPS_UNTIL_CLOSE):
        print(f'--------- Step #{step + 1} ---------')
        sim.step()

    # Call close
    print('==>==>==>==>==> CALLED CLOSED - NO MORE NEW ACTIONS <==<==<==<==<==')
    sim.close()

    # Run steps until finish
    step = STEPS_UNTIL_CLOSE + 1
    while sim.msgs_queue:
        step += 1
        print(f'--------- Step #{step} ---------')
        sim.step()

    # Print final state
    print("End:")
    print_summary()

def compute_final_db():
    # Collect all dbs from servers and combine them to the final DB.
    raise NotImplementedError

def print_step_summary():
    print(f'\n :: Step Summary :: \n'
          f'    Num Servers: {len(simulation_state.servers)}\n'
          f'    Num Clients: {len(simulation_state.clients)}\n'
          f'    Faulty: {simulation_state.faulty_counter}\n'
          f' :: :::::::::::: :: ')
    print('\n\n')


def print_summary():
    print("\n---------- SUMMARY ----------")
    print(f"Num Servers: {len(simulation_state.servers)}")
    print(f"Num Clients: {len(simulation_state.clients)}")
    print(f"Faulty: {simulation_state.faulty_counter}")
    print("---------- ---------- ----------\n")
    for agent in simulation_state.get_all_agents():
        if agent.role == AgentRole.CLIENT:
            print(f"Client: {agent.id}")
        elif agent.role == AgentRole.SERVER:
            print(f"Server: {agent.id}")
        print(f"Tokens: {agent.my_tokens}")

def check_liveness():
    # Liveness holds if the clients finished the execution of all the actions it performed.
    # That is, if the during_action property is True then an execution of some action has not finished.
    print('\n########## Liveness Assessment ##########')

    any_not_liveness = False
    for client in list(simulation_state.clients.values()):
        if client.is_faulty:
            print(f'Client ...{client.id[-4:]} is faulty ------------------------> LIVENESS IRRELEVANT')
        else:
            if client.during_action:
                any_not_liveness = True
                print(f'Client ...{client.id[-4:]} did NOT finished all executions --> LIVENESS DOESN\'T HOLD')
                print(f'Client has the following upons: {[entry[0].__name__ for entry in client.upon_registry]}')
            else:
                print(f'Client ...{client.id[-4:]} finished all executions ----------> LIVENESS HOLDS')

    if any_not_liveness:
        print('\n====> LIVENESS Property DOESN\'T HOLD... :(\n')
        return False
    else:
        print('\n====> LIVENESS Property HOLDS. :)\n')
        return True


NUM_SIMULATIONS = 1
STEPS_UNTIL_CLOSE = 200

liveness_results = []
for sim_counter in range(NUM_SIMULATIONS):
    print(f'~~~~~~~~~~ SIMULATION #{sim_counter + 1} ~~~~~~~~~~')

    """
    Run with omissions
    """
    simulation_state.ALLOW_FAULTY = True
    simulation_state.CLIENT_GET_RATE = 0
    simulation_state.CLIENT_PAY_RATE = 0.5
    simulation_state.CLIENT_OMISSION_RATE = 0.3
    simulation_state.SERVER_OMISSION_RATE = 0.8
    simulation_state.TRANSFORM_RATE = 0.2

    final_db_omissions = run_simulation_test()

    # Liveness and Safety Checks
    liveness = check_liveness()
    liveness_results.append(liveness)

    """
    Run withOUT omissions
    """
    # TODO: Uncomment
    # simulation_state.ALLOW_FAULTY = False
    # simulation_state.CLIENT_GET_RATE = 0
    # simulation_state.CLIENT_PAY_RATE = 0.3
    # simulation_state.CLIENT_OMISSION_RATE = 0.3  # 0.3
    # simulation_state.SERVER_OMISSION_RATE = 0.8  # 0.8
    # simulation_state.TRANSFORM_RATE = 0.5
    #
    # final_db_no_omissions = run_simulation_test(TOTAL_STEPS, STOP_COMM_AFTER_STEPS)
    #
    # check_liveness()

    # TODO: Make sure final_db_omissions == final_db_no_omissions

if all(liveness_results):
    print('Liveness HOLDS for ALL simulations!!! :)')
else:
    print('Liveness DOESN\'T hold for some simulations... :(')