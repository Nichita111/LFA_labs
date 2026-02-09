import random
from finite_automaton import FiniteAutomaton


class Grammar:
    def __init__(self, vn, vt, productions, start_symbol):
        self.vn = vn # V_N: set of non-terminal symbols
        self.vt = vt # V_T: set of terminal symbols
        self.productions = productions # P: dict{non-terminal: [list of right-hand sides]}
        self.start_symbol = start_symbol # S: start symbol

    def generate_string(self):
        result = []
        current = self.start_symbol

        while current in self.productions:
            production = random.choice(self.productions[current])
            # !WARNING! Not checked assumption:
            # As I saw from all variants I can assume that
            # the grammars are regular so the production rules are of the form A -> aB or A -> a
            # thus the first symbol is always terminal and the second (if exists) is non-terminal
            result.append(production[0])

            if len(production) == 2:
                # Production of the form aB (terminal + non-terminal)
                current = production[1]
            else:
                # Production of the form a (terminal only) - stop
                break

        return ''.join(result)

    def to_finite_automaton(self):
        # just use the algorithm from the book
        final_state = 'X'

        states = self.vn | {final_state}
        alphabet = self.vt
        start_state = self.start_symbol
        final_states = {final_state}

        transitions = {}
        for non_terminal, rules in self.productions.items():
            for rule in rules:
                terminal = rule[0]
                key = (non_terminal, terminal)

                if len(rule) == 2:
                    next_state = rule[1]
                else:
                    next_state = final_state

                if key not in transitions:
                    transitions[key] = set()
                transitions[key].add(next_state)

        return FiniteAutomaton(states, alphabet, transitions, start_state, final_states)
