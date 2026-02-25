# Determinism in Finite Automata. Conversion from NDFA to DFA. Chomsky Hierarchy.

### Course: Formal Languages & Finite Automata
### Author: Nichita Rusnac

----

## Theory

A **finite automaton** (FA) is a mathematical model of computation consisting of a finite set of states, an input alphabet, a transition function, a start state, and a set of accepting (final) states. It reads an input string symbol by symbol and transitions between states according to the transition function. If, after consuming all input symbols, the automaton is in a final state, the string is accepted.

There are two types of finite automata based on the transition function:
- **Deterministic Finite Automaton (DFA):** For every state and input symbol, there is exactly one next state. The behavior is fully predictable.
- **Non-deterministic Finite Automaton (NDFA/NFA):** For a given state and input symbol, there may be zero, one, or multiple possible next states. While this introduces ambiguity in the transitions, every NDFA can be converted to an equivalent DFA using the **subset construction** algorithm.

The **Chomsky hierarchy** classifies formal grammars into four types:
- **Type 0 (Unrestricted):** No restrictions on production rules.
- **Type 1 (Context-Sensitive):** For every production α → β, |α| ≤ |β| (with a possible exception for S → ε).
- **Type 2 (Context-Free):** All productions have a single non-terminal on the left-hand side.
- **Type 3 (Regular):** Productions are either all right-linear (A → aB | a) or all left-linear (A → Ba | a). Regular grammars correspond directly to finite automata.

A key result in formal language theory is that regular grammars and finite automata are equivalent — any regular grammar can be converted to an FA and vice versa.

## Objectives:

* Implement a function that classifies a grammar based on the Chomsky hierarchy.
* Implement conversion of a finite automaton to a regular grammar.
* Determine whether a given FA is deterministic or non-deterministic.
* Implement conversion of an NDFA to a DFA.
* Represent the finite automaton graphically (bonus).


## Implementation description

### Variant 20 — Finite Automaton Definition

The FA from Variant 20 is defined as:
- Q = {q0, q1, q2, q3}
- Σ = {a, b, c}
- F = {q3}
- δ(q0, a) = q0
- δ(q0, a) = q1
- δ(q1, b) = q2
- δ(q2, a) = q2
- δ(q2, c) = q3
- δ(q3, c) = q3

In `main.py`, this is represented using Python sets and a dictionary mapping `(state, symbol)` pairs to sets of next states. Note that δ(q0, a) maps to **both** q0 and q1, which makes this automaton non-deterministic.

```python
states = {'q0', 'q1', 'q2', 'q3'}
alphabet = {'a', 'b', 'c'}
final_states = {'q3'}
start_state = 'q0'
transitions = {
    ('q0', 'a'): {'q0', 'q1'},  # δ(q0,a) = q0, δ(q0,a) = q1
    ('q1', 'b'): {'q2'},         # δ(q1,b) = q2
    ('q2', 'a'): {'q2'},         # δ(q2,a) = q2
    ('q2', 'c'): {'q3'},         # δ(q2,c) = q3
    ('q3', 'c'): {'q3'},         # δ(q3,c) = q3
}
```

---

### Task 2a: Chomsky Hierarchy Classification

The `classify()` method in the `Grammar` class determines the grammar type by checking from the most restrictive (Type 3) to the least restrictive (Type 0). It delegates to three helper methods: `_is_type3()`, `_is_type2()`, and `_is_type1()`.

```python
def classify(self):
    if self._is_type3():
        return "Type 3 (Regular Grammar)"
    if self._is_type2():
        return "Type 2 (Context-Free Grammar)"
    if self._is_type1():
        return "Type 1 (Context-Sensitive Grammar)"
    return "Type 0 (Unrestricted Grammar)"
```

For **Type 3** (regular), the method verifies that all productions are either right-linear (A → aB or A → a) or left-linear (A → Ba or A → a), but not a mix of both. Left-hand sides must all be single non-terminals.

```python
def _is_type3(self):
    has_right_linear = False
    has_left_linear = False

    for lhs, rhs_list in self.productions.items():
        if lhs not in self.vn:
            return False
        for rhs in rhs_list:
            if rhs == '' or rhs == 'ε':
                continue
            if len(rhs) == 1:
                if rhs in self.vt:
                    continue
                else:
                    return False
            if len(rhs) == 2:
                if rhs[0] in self.vt and rhs[1] in self.vn:
                    has_right_linear = True
                elif rhs[0] in self.vn and rhs[1] in self.vt:
                    has_left_linear = True
                else:
                    return False
                continue
            # ... handles longer productions similarly
    if has_right_linear and has_left_linear:
        return False
    return True
```

For **Type 2** (context-free), only the LHS is checked — it must be a single non-terminal:

```python
def _is_type2(self):
    for lhs in self.productions:
        if lhs not in self.vn:
            return False
    return True
```

For **Type 1** (context-sensitive), two constraints are checked: ε must not appear on any right-hand side, and for every production α → β the length constraint |α| ≤ |β| must hold:

```python
def _is_type1(self):
    for lhs, rhs_list in self.productions.items():
        for rhs in rhs_list:
            if rhs == '' or rhs == 'ε':
                return False
            elif len(lhs) > len(rhs):
                return False
    return True
```

The classifier is demonstrated on three grammars in `main.py` — a regular grammar (converted from the FA), a context-free grammar (`S → aSb | ab`), and a context-sensitive grammar (`AB → aAB | ab`).

---

### Task 3a: FA → Regular Grammar Conversion

The `to_regular_grammar()` method converts the finite automaton to a right-linear regular grammar. Each FA state is mapped to a non-terminal (q0 → S, q1 → A, q2 → B, q3 → C), and for each transition δ(q, a) = p, a production Q → aP is created. If p is a final state, an additional production Q → a is added.

```python
def to_regular_grammar(self):
    state_list = sorted(self.states, key=lambda s: (s != self.start_state, s))
    state_map = {}
    state_map[state_list[0]] = 'S'
    available = [chr(c) for c in range(ord('A'), ord('Z') + 1) if chr(c) != 'S']
    idx = 0
    for state in state_list[1:]:
        state_map[state] = available[idx]
        idx += 1

    vn = set(state_map.values())
    vt = set(self.alphabet)
    productions = {}

    for (state, symbol), next_states in self.transitions.items():
        lhs = state_map[state]
        if lhs not in productions:
            productions[lhs] = []
        for ns in next_states:
            rhs = symbol + state_map[ns]
            if rhs not in productions[lhs]:
                productions[lhs].append(rhs)
            if ns in self.final_states:
                if symbol not in productions[lhs]:
                    productions[lhs].append(symbol)

    return Grammar(vn, vt, productions, 'S'), state_map
```

**Resulting grammar:**
| State mapping | Productions |
|---|---|
| q0 → S | S → aS \| aA |
| q1 → A | A → bB |
| q2 → B | B → aB \| cC \| c |
| q3 → C | C → cC \| c |

---

### Task 3b: Determinism Check

The `is_deterministic()` method checks whether each `(state, symbol)` pair maps to at most one next state. If any pair has multiple targets, the automaton is non-deterministic.

```python
def is_deterministic(self):
    for (_, _), next_states in self.transitions.items():
        if len(next_states) > 1:
            return False
    return True
```

For Variant 20, δ(q0, a) = {q0, q1} — reading symbol 'a' in state q0 can lead to **two** different states, so the automaton is **non-deterministic (NDFA)**.

---

### Task 3c: NDFA → DFA Conversion

The `to_dfa()` method implements the **subset construction** algorithm. It explores sets of NFA states reachable from each combined state, using a BFS approach. Each DFA state is a set of NFA states. A DFA state is final if it contains at least one NFA final state.

```python
def to_dfa(self):
    start = frozenset({self.start_state})
    dfa_states = set()
    dfa_transitions = {}
    queue = [start]
    dfa_states.add(start)

    while queue:
        current = queue.pop(0)
        for symbol in self.alphabet:
            next_state = frozenset(
                ns for state in current
                for ns in self.transitions.get((state, symbol), set())
            )
            if not next_state:
                continue

            if next_state not in dfa_states:
                dfa_states.add(next_state)
                queue.append(next_state)

            dfa_transitions[(current, symbol)] = {next_state}

    dfa_final = {s for s in dfa_states if s & self.final_states}
    # ... rename states to D0, D1, ... and build new FiniteAutomaton
```

**Subset construction result:**

| DFA State | NFA States | 
|---|---|
| D0 | {q0} |
| D1 | {q2} |
| D2 | {q3} |
| D3 | {q0, q1} |

**DFA transitions:**

| δ | a | b | c |
|---|---|---|---|
| D0 | D3 | — | — |
| D1 | D1 | — | D2 |
| D2 | — | — | D2 |
| D3 | D3 | D1 | — |

Final state: **D2** (contains q3).

The resulting DFA is confirmed to be deterministic — every `(state, symbol)` pair maps to at most one next state.

---

### Task 3d: Graphical Representation (Bonus)

The `display()` method uses the `graphviz` library to generate a visual diagram of the automaton. It creates nodes for each state (double circles for final states), draws edges with transition labels, and merges parallel edges into a single labeled edge for clarity.

```python
def display(self, filename='finite_automaton', view=False):
    try:
        from graphviz import Digraph
    except ImportError:
        print("graphviz package not installed.")
        return None

    dot = Digraph(comment='Finite Automaton')
    dot.attr(rankdir='LR', size='10,5')

    dot.node('start', shape='none', label='')
    dot.edge('start', self.start_state)

    for state in sorted(self.states):
        if state in self.final_states:
            dot.node(state, shape='doublecircle')
        else:
            dot.node(state, shape='circle')

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

    dot.render(filename, format='png', cleanup=True, view=view)
```

The method generates DOT source files (`nfa_variant20.dot` and `dfa_variant20.dot`) which can be rendered with the Graphviz system tool or visualized online at https://dreampuf.github.io/GraphvizOnline/.

---

### String Validation

To verify the equivalence of the NFA and the converted DFA, both are tested against the same set of strings:

```
  String          NFA          DFA          Match
  --------------------------------------------------
  'abc'           ACCEPTED     ACCEPTED     OK
  'aabcc'         ACCEPTED     ACCEPTED     OK
  'abac'          ACCEPTED     ACCEPTED     OK
  'abacc'         ACCEPTED     ACCEPTED     OK
  'aaabaaac'      ACCEPTED     ACCEPTED     OK
  'ab'            REJECTED     REJECTED     OK
  'acc'           REJECTED     REJECTED     OK
  'b'             REJECTED     REJECTED     OK
  ''              REJECTED     REJECTED     OK
  'ababc'         REJECTED     REJECTED     OK
```

All 10 test strings produce matching results between the NFA and DFA, confirming the correctness of the subset construction conversion.


## Conclusions / Results

In this laboratory work, all tasks from Lab 2 were successfully implemented:

1. **Chomsky Hierarchy Classification** — The `classify()` method correctly identifies grammars from Type 0 through Type 3 by checking structural constraints on productions in order of restrictiveness. The grammar converted from the Variant 20 FA is correctly classified as Type 3 (Regular).

2. **FA → Regular Grammar** — The conversion maps each FA state to a non-terminal and each transition to a production rule, producing a valid right-linear grammar: S → aS | aA, A → bB, B → aB | cC | c, C → cC | c.

3. **Determinism Check** — The automaton from Variant 20 is correctly identified as non-deterministic due to the transition δ(q0, a) = {q0, q1}.

4. **NDFA → DFA** — The subset construction algorithm produces a 4-state DFA (D0, D1, D2, D3) that is verified to be deterministic and to accept exactly the same language as the original NDFA.

5. **Graphical Representation** — The `display()` method generates Graphviz DOT source for both the NFA and DFA, which can be rendered into diagrams.

Thus it was a great experience and it helped me understand better the theoretical knowledge about the NFA, DFA and Chomsky.

## References

1. Hopcroft, J.E., Motwani, R., Ullman, J.D. — *Introduction to Automata Theory, Languages, and Computation*
2. Course materials — Formal Languages & Finite Automata, TUM
3. Graphviz documentation — https://graphviz.org/documentation/
