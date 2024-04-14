import uuid

import simulation_state

class Agent:
    def __init__(self, is_server):
        self.is_server = is_server
        self.is_faulty = False
        self.tokens_db = None
        self.my_tokens = []

        self.id = self.generate_id()

    @staticmethod
    def generate_id():
        owner_name = str(uuid.uuid4())
        simulation_state.owner_names.append(owner_name)
        return owner_name

    def set_tokens_db(self, tokens_db):
        self.tokens_db = tokens_db

        # Initialize my tokens from the whole dictionary
        for token in list(self.tokens_db.values()):
            if token.owner == self.id:
                self.my_tokens.append(token.id)

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
        if self.is_faulty:
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
            self.is_faulty = self.decide_is_faulty()
            # !updated to server/client lists!
            # !updated to faulty list!
            raise NotImplementedError('Transform server to client logic.')
        else:
            self.is_server = True
            # !updated to server/client lists!
            # !updated to faulty list!
            raise NotImplementedError('Transform client to server logic.')

    def decide_is_faulty(self):
        max_faulty = int(len(simulation_state.servers)/2)
        if len(simulation_state.faulty) < max_faulty:
            simulation_state.faulty.append(self.id)
            return True
        return False
