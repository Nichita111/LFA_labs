from finite_automaton import FiniteAutomaton
from grammar import Grammar


def main():
    print("  Lab 2: Determinism in Finite Automata")
    print("  Variant 20")
    #Define the NFA from Variant 20

    states = {'q0', 'q1', 'q2', 'q3'}
    alphabet = {'a', 'b', 'c'}
    final_states = {'q3'}
    start_state = 'q0'
    transitions = {
        ('q0', 'a'): {'q0', 'q1'},
        ('q2', 'a'): {'q2'},
        ('q1', 'b'): {'q2'},
        ('q2', 'c'): {'q3'},
        ('q3', 'c'): {'q3'},
    }

    fa = FiniteAutomaton(states, alphabet, transitions, start_state, final_states)
    print("\nOriginal Finite Automaton (Variant 20)")
    print(fa)

    # Task 3b: Check determinism
    print(" \n Task 3b: Determinism Check")
    if fa.is_deterministic():
        print("The FA is DETERMINISTIC (DFA).")
    else:
        print("The FA is NON-DETERMINISTIC (NDFA).")
        print("Non-deterministic transitions:")
        for (state, symbol), next_states in sorted(fa.transitions.items()):
            if len(next_states) > 1:
                print(f"  δ({state}, {symbol}) = {{{', '.join(sorted(next_states))}}}")

    # Task 3a: Convert FA to Regular Grammar
    print("\n  Task 3a: FA → Regular Grammar Conversion")
    grammar, state_map = fa.to_regular_grammar()
    print("State → Non-terminal mapping:")
    for state, nt in sorted(state_map.items()):
        print(f"  {state} → {nt}")
    print()
    print(grammar)

    # Task 2a: Chomsky Hierarchy Classificatio
    print("\n")
    print("  Task 2a: Chomsky Hierarchy Classification")
    print(f"The converted grammar is: {grammar.classify()}")

    # Task 3c: NDFA → DFA Conversion
    print("\n")
    print("  Task 3c: NDFA → DFA Conversion")
    dfa, dfa_state_map = fa.to_dfa()

    print("Subset construction — state mapping:")
    for dfa_name in sorted(dfa_state_map):
        original = dfa_state_map[dfa_name]
        print(f"  {dfa_name} = {{{', '.join(sorted(original))}}}")

    print()
    print(dfa)
    print(f"\nResulting DFA is deterministic: {dfa.is_deterministic()}")

    #Verify NFA and DFA equivalence on test strings
    print("\n")
    print("  String Validation: NFA vs DFA Comparison")
    test_strings = [
        "abc",       # q0→q1(a), q1→q2(b), q2→q3(c)              → ACCEPTED
        "aabcc",     # q0→q0(a)→q1(a), q1→q2(b), q2→q3(c)→q3(c) → ACCEPTED
        "abac",      # q0→q1(a), q1→q2(b), q2→q2(a), q2→q3(c)   → ACCEPTED
        "abacc",     # same as above + q3→q3(c)                   → ACCEPTED
        "aaabaaac",  # long chain of a's before and after b        → ACCEPTED
        "ab",        # ends at q2 (not final)                      → REJECTED
        "acc",       # no 'c' transition from q0 or q1             → REJECTED
        "b",         # no 'b' transition from q0                   → REJECTED
        "",          # q0 is not a final state                     → REJECTED
        "ababc",     # q2 has no 'b' transition                    → REJECTED
    ]

    print(f"  {'String':<15} {'NFA':<12} {'DFA':<12} {'Match'}")
    for s in test_strings:
        nfa_result = fa.string_belongs_to_language(s)
        dfa_result = dfa.string_belongs_to_language(s)
        nfa_str = 'ACCEPTED' if nfa_result else 'REJECTED'
        dfa_str = 'ACCEPTED' if dfa_result else 'REJECTED'
        match_str = 'OK' if nfa_result == dfa_result else 'MISMATCH!'
        display_s = f"'{s}'" if s else "''"
        print(f"  {display_s:<15} {nfa_str:<12} {dfa_str:<12} {match_str}")

    #Task 3d: Graphical Representation (Bonus)
    print("  Task 3d: Graphical Representation (Bonus)")
    print("Generating NFA graph...")
    fa.display(filename='nfa_variant20')
    print("Generating DFA graph...")
    dfa.display(filename='dfa_variant20')

if __name__ == '__main__':
    main()
