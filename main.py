#!/usr/bin/env python3
import copy
import pickle

from interfaces import AgentRole, MessageType
from simulator import Simulator
import simulation_state


def run_simulation_test():
    sim = Simulator()
    simulation_state.step_counter = 0

    # Print starting state
    print("Start:")
    print_summary()

    # Run steps until close
    for _ in range(simulation_state.STEPS_UNTIL_CLOSE):
        simulation_state.step_counter += 1
        print(f'--------- Step #{simulation_state.step_counter + 1} ---------')
        sim.step()

    # Call close
    if not simulation_state.LOG_RUN:
        print('==>==>==>==>==> CALLED CLOSED - NO MORE NEW ACTIONS <==<==<==<==<==')
        sim.close()

    # Run steps until finish
    while sim.msgs_queue or (simulation_state.LOG_RUN and len(simulation_state.action_log) > 0):
        simulation_state.step_counter += 1
        if simulation_state.step_counter > simulation_state.STEPS_UNTIL_INFTY_LOOP:
            print('Infinite loop detected. Exiting...')
            break
        print(f'--------- Step #{simulation_state.step_counter + 1} ---------')
        sim.step()

    # Print final state
    print("End:")
    print_summary()

    # Print the log
    print_action_log()

    return compute_final_db()

def compute_final_db():
    final_db = {}
    for server in simulation_state.servers.values():
        for token_id, token in server.tokens_db.items():
            if token_id not in final_db:
                final_db[token_id] = copy.deepcopy(token)
            elif token.version > final_db[token_id].version:
                final_db[token_id] = copy.deepcopy(token)
    return final_db

def check_safety(token_db_1, token_db_2):
    if len(token_db_1) != len(token_db_2):
        print('Safety DOESN\'T hold... :( :: Not Same Length.')
        return False
    elif set(token_db_1.keys()) != set(token_db_2.keys()):
        print('Safety DOESN\'T hold... :( :: Not equal token lists.')
        return False

    for token_id in token_db_1.keys():
        if token_db_1[token_id].id != token_db_2[token_id].id:
            print('Safety DOESN\'T hold... :( :: ID Missmatch')
            return False
        elif token_db_1[token_id].version != token_db_2[token_id].version:
            print('Safety DOESN\'T hold... :( ::  Version Missmatch')
            return False
        elif token_db_1[token_id].owner != token_db_2[token_id].owner:
            print('Safety DOESN\'T hold... :( :: Owner Missmatch')
            return False

    print('Safety HOLDS!!! :)')
    return True

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
        print(f"Tokens: {[token.id for token in agent.my_tokens]}")

def print_action_log():
    print("\n---------- Action Log ----------")
    for action in simulation_state.action_log:
        print(f"Agent: {action[0]}")
        print(f"Timestamp: {action[2]}")
        print(f"Action: {action[1]}")
        print("-----------------------------")
    print("---------- ---------- ----------\n")

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


liveness_results = []
safety_results = []

for sim_counter in range(simulation_state.NUM_SIMULATIONS):
    print(f'~~~~~~~~~~ SIMULATION #{sim_counter + 1} ~~~~~~~~~~')

    """
    Run with omissions
    """
    simulation_state.LOG_RUN = 0
    simulation_state.READ_FROM_LOG = simulation_state.LOG_RUN
    simulation_state.WRITE_TO_LOG = 1 - simulation_state.READ_FROM_LOG
    simulation_state.ALLOW_FAULTY = True #True
    simulation_state.CLIENT_GET_RATE = 0
    simulation_state.CLIENT_PAY_RATE = 0.5
    simulation_state.CLIENT_OMISSION_RATE = 0.1 #0.3
    simulation_state.SERVER_OMISSION_RATE = 0.8
    simulation_state.CLIENT_TRANSFORM_RATE = 0.1
    simulation_state.SERVER_TRANSFORM_RATE = 0.1

    final_db_omissions = run_simulation_test()

    # Liveness and Safety Checks
    liveness = check_liveness()
    liveness_results.append(liveness)

    """
    Run withOUT omissions
    """
    simulation_state.LOG_RUN = 1
    simulation_state.READ_FROM_LOG = simulation_state.LOG_RUN
    simulation_state.WRITE_TO_LOG = 1 - simulation_state.READ_FROM_LOG
    simulation_state.ALLOW_FAULTY = False
    simulation_state.CLIENT_GET_RATE = 0
    simulation_state.CLIENT_PAY_RATE = 0.5
    simulation_state.CLIENT_OMISSION_RATE = 0  # 0.3
    simulation_state.SERVER_OMISSION_RATE = 0  # 0.8
    CLIENT_TRANSFORM_RATE = 0.1  # 0.1
    SERVER_TRANSFORM_RATE = 0.1  # 0.1

    final_db_no_omissions = run_simulation_test()

    liveness = check_liveness()
    liveness_results.append(liveness)

    safety = check_safety(final_db_omissions, final_db_no_omissions)
    safety_results.append(safety)


# ############### Linearization Test ###############
print('############### Linearization Test ###############')
# Scenario 1:
#   Client A initiates GET_TOKENS request
#   Client B initiates PAY request
#   Client B's PAY requests reaches the linearizability point
#   Client A's GET_TOKENS request finishes
#   Client B's PAY request finishes.
#
# Scenario 2:
#   Client A initiates GET_TOKENS request
#   Client B initiates PAY request
#   Client B's PAY requests reaches the linearizability point
#   Client B's PAY request finishes.
#   Client A's GET_TOKENS request finishes
#
lin_test_scenario_a_log, lin_test_scenario_b_log = pickle.load(open('lin_test.pkl', 'rb'))
"""
Run with omissions
"""
simulation_state.LOG_RUN = 1
simulation_state.READ_FROM_LOG = simulation_state.LOG_RUN
simulation_state.WRITE_TO_LOG = 1 - simulation_state.READ_FROM_LOG
simulation_state.ALLOW_FAULTY = True #True
simulation_state.CLIENT_GET_RATE = 0
simulation_state.CLIENT_PAY_RATE = 0.3
simulation_state.CLIENT_OMISSION_RATE = 0.1 #0.3
simulation_state.SERVER_OMISSION_RATE = 0.8
simulation_state.CLIENT_TRANSFORM_RATE = 0.1
simulation_state.SERVER_TRANSFORM_RATE = 0.1

simulation_state.action_log = lin_test_scenario_a_log

final_db_omissions = run_simulation_test()

# Liveness and Safety Checks
liveness = check_liveness()
liveness_results.append(liveness)

"""
Run withOUT omissions
"""
simulation_state.LOG_RUN = 1
simulation_state.READ_FROM_LOG = simulation_state.LOG_RUN
simulation_state.WRITE_TO_LOG = 1 - simulation_state.READ_FROM_LOG
simulation_state.ALLOW_FAULTY = False
simulation_state.CLIENT_GET_RATE = 0
simulation_state.CLIENT_PAY_RATE = 0.3
simulation_state.CLIENT_OMISSION_RATE = 0  # 0.3
simulation_state.SERVER_OMISSION_RATE = 0  # 0.8
CLIENT_TRANSFORM_RATE = 0.1  # 0.1
SERVER_TRANSFORM_RATE = 0.1  # 0.1

simulation_state.action_log = lin_test_scenario_b_log

final_db_no_omissions = run_simulation_test()

liveness = check_liveness()
liveness_results.append(liveness)

safety = check_safety(final_db_omissions, final_db_no_omissions)
safety_results.append(safety)


print()
print('-'*100)
print()

if all(liveness_results):
    print('Liveness HOLDS for ALL simulations!!! :)')
else:
    print('Liveness DOESN\'T hold for some simulations... :(')

if all(safety_results):
    print('Safety HOLDS for ALL simulations!!! :)')
else:
    print('Safety DOESN\'T hold for some simulations... :(')