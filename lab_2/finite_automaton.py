from grammar import Grammar


class FiniteAutomaton:
    def __init__(self, states, alphabet, transitions, start_state, final_states):
        self.states = states
        self.alphabet = alphabet
        self.transitions = transitions
        self.start_state = start_state
        self.final_states = final_states

    def string_belongs_to_language(self, input_string):
        current_states = {self.start_state}

        for symbol in input_string:
            next_states = set()
            for state in current_states:
                key = (state, symbol)
                if key in self.transitions:
                    next_states.update(self.transitions[key])
            current_states = next_states

            if not current_states:
                return False

        return bool(current_states & self.final_states)

    def is_deterministic(self):
        # is deterministic if for every (state, symbol) pair, there is just one next state
        for (_, _), next_states in self.transitions.items():
            if len(next_states) > 1:
                return False
        return True

    def to_regular_grammar(self):
        """
        Algorithm:
        - For each transition δ(q, a) = p:  add production Q → aP
        - For each transition δ(q, a) = p where p ∈ F:  also add Q → a

        Returns:
            Tuple of (Grammar, state_mapping_dict)
        """
        # Map FA states to single uppercase letters for grammar non-terminals
        state_list = sorted(self.states, key=lambda s: (s != self.start_state, s)) #[q0,q1,q2]
        state_map = {}
        state_map[state_list[0]] = 'S'  # start state always maps to 'S'
        available = [chr(c) for c in range(ord('A'), ord('Z') + 1) if chr(c) != 'S']
        idx = 0
        for state in state_list[1:]:
            state_map[state] = available[idx] # q1: A (just because i don't like q0,q1,...)
            idx += 1

        vn = set(state_map.values())
        vt = set(self.alphabet)
        productions = {}

        for (state, symbol), next_states in self.transitions.items():
            lhs = state_map[state]
            if lhs not in productions:
                productions[lhs] = []
            for ns in next_states:
                # Add A → aB
                rhs = symbol + state_map[ns]
                if rhs not in productions[lhs]:
                    productions[lhs].append(rhs)
                # If the next state is final, also add A → a
                if ns in self.final_states:
                    if symbol not in productions[lhs]:
                        productions[lhs].append(symbol)

        return Grammar(vn, vt, productions, 'S'), state_map

    def to_dfa(self):
        """

        Algorithm:
        1. Start with the set containing only the NFA start state.
        2. For each set of states and each symbol, compute the set of reachable states.
        3. Repeat until no new sets are discovered.
        4. A DFA state is final if it contains any NFA final state.

        Returns:
            Tuple of (DFA as FiniteAutomaton, state_mapping_dict)
            where state_mapping maps DFA state names to sets of original NFA states.
        """
        start = frozenset({self.start_state})
        dfa_states = set()
        dfa_transitions = {}
        queue = [start]
        dfa_states.add(start) # {[q0]}

        while queue:
            current = queue.pop(0)
            for symbol in self.alphabet:
                next_state = frozenset(
                    ns for state in current
                    for ns in self.transitions.get((state, symbol), set())
                )
                if not next_state:
                    continue  # no transition for this symbol — skip

                if next_state not in dfa_states:
                    dfa_states.add(next_state)
                    queue.append(next_state)

                dfa_transitions[(current, symbol)] = {next_state}

        # Final states: any DFA state that contains at least one NFA final state
        dfa_final = {s for s in dfa_states if s & self.final_states}

        # Generate readable names (D0, D1, ...) for DFA states
        sorted_states = sorted(dfa_states, key=lambda s: (len(s), sorted(s)))
        state_map = {}
        for i, state in enumerate(sorted_states):
            state_map[state] = f"D{i}"

        # Build renamed DFA
        new_states = set(state_map.values())
        new_transitions = {}
        for (state, symbol), next_states_set in dfa_transitions.items():
            for ns in next_states_set:
                new_transitions[(state_map[state], symbol)] = {state_map[ns]}
        new_final = {state_map[s] for s in dfa_final}
        new_start = state_map[start]

        dfa = FiniteAutomaton(new_states, set(self.alphabet), new_transitions, new_start, new_final)

        # Readable mapping: DFA state name → set of original NFA states
        readable_map = {state_map[k]: set(k) for k in state_map}

        return dfa, readable_map

    def display(self, filename='finite_automaton'):
        """
        Display the finite automaton graphically using graphviz.

        Args:
            filename: Output filename (without extension)

        Returns:
            The Digraph object
        """
        from graphviz import Digraph

        dot = Digraph(comment='Finite Automaton')
        dot.attr(rankdir='LR', size='10,5')

        # Invisible start node for the entry arrow
        dot.node('start', shape='none', label='')
        dot.edge('start', self.start_state)

        # Add state nodes
        for state in sorted(self.states):
            if state in self.final_states:
                dot.node(state, shape='doublecircle')
            else:
                dot.node(state, shape='circle')

        # Merge transitions with the same source and target into one labeled edge
        edge_labels = {}
        for (src, symbol), targets in self.transitions.items():
            for tgt in targets:
                key = (src, tgt)
                if key in edge_labels:
                    edge_labels[key].append(symbol)
                else:
                    edge_labels[key] = [symbol]

        for (src, tgt), labels in edge_labels.items():
            dot.edge(src, tgt, label=', '.join(sorted(labels)))

        dot.render(filename, format='png', cleanup=True)
        print(f"Graph saved as {filename}.png")
        return dot

    def __str__(self):
        lines = [
            f"Finite Automaton:",
            f"  States (Q): {{{', '.join(sorted(self.states))}}}",
            f"  Alphabet (Σ): {{{', '.join(sorted(self.alphabet))}}}",
            f"  Start state (q0): {self.start_state}",
            f"  Final states (F): {{{', '.join(sorted(self.final_states))}}}",
            f"  Transitions (δ):",
        ]
        for (state, symbol), next_states in sorted(self.transitions.items()):
            lines.append(f"    δ({state}, {symbol}) = {{{', '.join(sorted(next_states))}}}")
        return '\n'.join(lines)
