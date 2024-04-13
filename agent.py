import simulation_state

class Agent:
    def __init__(self, name, is_server, token_alloc):
        self.name = name
        self.is_server = is_server
        self.token_alloc = token_alloc
        self.is_faulty = False

    def step(self, incoming_messages):
        outgoing_messages = []

        # 1. Hendle incoming messages
        outgoing_messages += self.handle_incoming(incoming_messages)

        # 2. Transform
        if self.should_transform():
            self.transform()

        # 3. If client, do some action
        if not self.is_server:
            # If is client after transform, then can create pay messages
            # !Only after performing gettokens!
            # Some logic on generating pay messages
            pass

        # 4. Decide if faulty, and if faulty clear outgoing_messages
        if self.decide_is_faulty():
            outgoing_messages = []

        return outgoing_messages

    def handle_incoming(self, incoming_messages):
        # Perform client/server logic based on incoming messages
        # Return new messages based on that logic.
        pass

    def should_transform(self):
        # Decides weather should transform (randomly?) using simulation_state.num_servers, simulation_state.num_clients
        pass

    def transform(self):
        if self.is_server:
            self.is_server = False
            raise NotImplementedError('Transform server to client logic.')
        else:
            self.is_server = True
            raise NotImplementedError('Transform client to server logic.')

    def decide_is_faulty(self):
        # randomly decide if should be faulty based using simulation_state.num_servers
        pass
