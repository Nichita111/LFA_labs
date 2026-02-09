class FiniteAutomaton:
    def __init__(self, states, alphabet, transitions, start_state, final_states):
        self.states = states # Q: set of states
        self.alphabet = alphabet #Sigma: set of terminal symbols
        self.transitions = transitions # delta: dict {(state, symbol): set of next states}
        self.start_state = start_state # q0: initial state
        self.final_states = final_states # F: set of accepting states

    # pain in the finite automata function, but I guess it's not that bad    
    def string_belongs_to_language(self, input_string):
        current_states = {self.start_state}

        # go through each symbol
        for symbol in input_string:
            next_states = set()
            for state in current_states:
                # check if there's a transition for this state and symbol
                key = (state, symbol)
                if key in self.transitions:
                    next_states.update(self.transitions[key])
            current_states = next_states

            # no transition then is just wrong string
            if not current_states:
                return False

        return bool(current_states & self.final_states)
