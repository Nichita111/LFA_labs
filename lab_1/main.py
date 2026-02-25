from grammar import Grammar


def main():
    # Grammar def
    vn = {'S', 'A', 'B', 'C'}
    vt = {'a', 'b', 'c', 'd'}

    productions = {
        'S': ['dA', 'dC'], # (S, d) -> {'A', 'C}
        'A': ['d', 'aB'], # (A, d) -> {'X'}
        'B': ['bC'], 
        'C': ['cA', 'aS'], #(C, c) -> {'A'}, (C, a) -> {'S'}
    }

    grammar = Grammar(vn, vt, productions, 'S')

    # Generate 5 valid strings
    print("5 strings generated from the grammar:")
    for i in range(5):
        word = grammar.generate_string()
        print(f"  {i + 1}. {word}")

    # Convert grammar to finite automaton
    fa = grammar.to_finite_automaton()

    print("\nFinite Automaton details:")
    print(f"  States: {fa.states}")
    print(f"  Alphabet: {fa.alphabet}")
    print(f"  Start state: {fa.start_state}")
    print(f"  Final states: {fa.final_states}")
    print(f"  Transitions:")
    for (state, symbol), next_states in sorted(fa.transitions.items()):
        print(f"    ({state}, {symbol}) -> {next_states}")

    # Test strings against the finite automaton
    test_strings = [
        "dd",           # S->dA, A->d                          => valid
        "dabcd",        # S->dA, A->aB, B->bC, C->cA, A->d    => valid
        "dabadd",       # as last but on step C do C->aS->dA->d  => valid
        "dabcabcd",     # as last but C->cA->aB->bC->cA->d       => valid
        "abc",          # doesn't start with 'd'               => invalid
        "dabba",        # invalid transition after 'b'         => invalid
        "",             # empty string                          => invalid
        "dabcadd",      # invalid: after C->cA->aB, 'd' fails => invalid
    ]

    print("\nString validation:")
    for s in test_strings:
        result = fa.string_belongs_to_language(s)
        print(f"  '{s}' -> {'ACCEPTED' if result else 'REJECTED'}")

if __name__ == '__main__':
    main()
