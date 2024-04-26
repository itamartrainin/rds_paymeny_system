#!/usr/bin/env python3

from interfaces import MessageType
from simulator import Simulator
import simulation_state


def run_simulation_test(total_steps, stop_comm_after_steps):
    sim = Simulator()

    print("Start:")
    for agent in simulation_state.get_all_agents():
        print(f"Agent: {agent.id}")
        print(f"Tokens: {agent.my_tokens}")

    for step in range(total_steps):
        print(f'--------- Step #{step + 1} ---------')
        # print('\n'.join(str(msg) for msg in sim.msgs_queue))

        if step == stop_comm_after_steps:
            print('==>==>==>==>==> COMMUNICATIONS CLOSED <==<==<==<==<==')
            sim.close()

        sim.step()

        # print_step_summary()

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
    for agent in simulation_state.get_all_agents():
        print(f"Agent: {agent.id}")
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
                print(f'Client ...{client.id[-4:]} did NOT finished all executions --> LIVENESS NOT HOLDS')
            else:
                print(f'Client ...{client.id[-4:]} finished all executions ----------> LIVENESS HOLDS')

    if any_not_liveness:
        print('\n====> LIVENESS Property does NOT hold... :(\n')
    else:
        print('\n====> LIVENESS Property does HOLDS. :)\n')


NUM_SIMULATIONS = 1
TOTAL_STEPS = 1000
STOP_COMM_AFTER_STEPS = TOTAL_STEPS/2

for sim_counter in range(NUM_SIMULATIONS):
    print(f'~~~~~~~~~~ SIMULATION #{sim_counter + 1} ~~~~~~~~~~')

    """
    Run with omissions
    """
    simulation_state.ALLOW_FAULTY = False # TODO: Change to FALSE!!!!!
    simulation_state.CLIENT_GET_RATE = 0
    simulation_state.CLIENT_PAY_RATE = 0.5
    simulation_state.CLIENT_OMISSION_RATE = 0  # 0.3
    simulation_state.FAULTY_OMISSION_RATE = 0  # 0.8
    simulation_state.TRANSFORM_RATE = 0.5

    final_db_omissions = run_simulation_test(TOTAL_STEPS, STOP_COMM_AFTER_STEPS)

    # Liveness and Safety Checks
    check_liveness()

    """
    Run withOUT omissions
    """
    # TODO: Uncomment
    # simulation_state.ALLOW_FAULTY = False
    # simulation_state.CLIENT_GET_RATE = 0
    # simulation_state.CLIENT_PAY_RATE = 0.3
    # simulation_state.CLIENT_OMISSION_RATE = 0.3  # 0.3
    # simulation_state.FAULTY_OMISSION_RATE = 0.8  # 0.8
    # simulation_state.TRANSFORM_RATE = 0.5
    #
    # final_db_no_omissions = run_simulation_test(TOTAL_STEPS, STOP_COMM_AFTER_STEPS)
    #
    # check_liveness()

    # TODO: Make sure final_db_omissions == final_db_no_omissions

