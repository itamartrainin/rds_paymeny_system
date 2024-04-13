import simulation_state

class Simulator:

    def __init__(self, num_start_clients, num_start_servers):
        simulation_state.num_clients = num_start_clients
        simulation_state.num_servers = num_start_servers

        self.agents = []
        self.active_messages = []

        self.init_agnets()

    def init_agnets(self):
        # create tokens
        # create initial token allocation
        # create agens according to simulation specifications
        pass

    def step(self):
        """
        1. For each message in active_messages decide if delivers on this step (async delay)
        2. For each agnet perform setep and collect new messages
        3. For each client message print performed actions
        """