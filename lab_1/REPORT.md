# Grammars and equivalence of them with FA

### Course: Formal Languages & Finite Automata
### Author: Rusnac Nichita

----

## Theory
A formal language is a system for writing and exchanging information using symbols and rules. It has three basic parts(sviataia troița):

Alphabet: the set of allowed characters (symbols).
Vocabulary: the words or tokens you can build from the alphabet.
Grammar: the rules that say which words and combinations are valid.

These parts can be chosen in many different ways depending on what the language should do. Picking different alphabets, vocabularies, or grammars produces different languages (for example natural languages, programming languages, or markup languages), and sometimes several languages can solve the same problem.

In the Chomsky classification of grammars there is an important type that we will work with in this laboratory. The type is the Regular Grammar. More specifically Right linear grammar defined as:
A -> aB
A -> a
where $a \in Vt$ and $A,B \in Vn$.
Thus i will use in this lab to simplify the code the fact that there is only one non-terminal in the right side of the transformation. And if there is a non-terminal character then the terminal one is always on the left(the first one).

Also an important topic from which i will use a Theorem is: Equivalence of the Regular Grammar with Finite Automata.

**Theorem:** It is given $ G = (V_N, V_T, P, S) $, where all productions are in the form

$$
A \to aA
$$
$$
A \to a,
$$
$$
A \in V_N, \quad a \in V_T
$$

For every regular grammar can be obtained equivalent finite automaton.

**Algorithm:**

1. Input alphabet is equal with set of terminal symbols  
   $\Sigma = V_T$.

2. The set of states is equal with set of non-terminal symbols and one additional state  
   $Q = V_N \cup \{X\}$, where $X$ is a new element, $X \in V_N$.

3. Initial state $q_0 = \{S\}$, $S$ - initial state.

4. Final state $F = \{X\}$.

5. It is built the set $\delta$: for all productions, which have representation  
   $A \to aB$, it is obtained:  
   $$
   \delta (A, a) = \delta (A, a) \cup \{B\}.
   $$

   For all productions which have representation $A \to a$, it is obtained:  
   $$
   \delta (A, a) = \delta (A, a) \cup \{X\}.
   $$


## Objectives:

1. Discover what a language is and what it needs to have in order to be considered a formal one;

2. Provide the initial setup for the evolving project that you will work on during this semester. You can deal with each laboratory work as a separate task or project to demonstrate your understanding of the given themes, but you also can deal with labs as stages of making your own big solution, your own project. Do the following:

    a. Create GitHub repository to deal with storing and updating your project;

    b. Choose a programming language. Pick one that will be easiest for dealing with your tasks, you need to learn how to solve the problem itself, not everything around the problem (like setting up the project, launching it correctly and etc.);

    c. Store reports separately in a way to make verification of your work simpler (duh)

3. According to your variant number, get the grammar definition and do the following:

    a. Implement a type/class for your grammar;

    b. Add one function that would generate 5 valid strings from the language expressed by your given grammar;

    c. Implement some functionality that would convert and object of type Grammar to one of type Finite Automaton;

    d. For the Finite Automaton, please add a method that checks if an input string can be obtained via the state transition from it;
   


## Implementation description

### Grammar class (`grammar.py`)

The Grammar class stores the four components of a formal grammar: the set of non-terminals vn, the set of terminals vt, the production rules productions (as a dictionary mapping each non-terminal to a list of its right-hand sides), and the start symbol. This representation makes it easy to look up all possible productions for any given non-terminal.

```python
class Grammar:
    def __init__(self, vn, vt, productions, start_symbol):
        self.vn = vn # V_N: set of non-terminal symbols
        self.vt = vt # V_T: set of terminal symbols
        self.productions = productions # P: dict{non-terminal: [list of right-hand sides]}
        self.start_symbol = start_symbol # S: start symbol
```

### String generation (`generate_string`)

The method starts from the start symbol and at each step randomly picks one of the available production rules for the current non-terminal. Since the grammar is right-linear, the first character of every production is always a terminal (which gets appended to the result), and the optional second character is the next non-terminal to continue from. The process stops when a terminal-only production is selected.

```python
def generate_string(self):
    result = []
    current = self.start_symbol

    while current in self.productions:
        production = random.choice(self.productions[current])
        result.append(production[0])

        if len(production) == 2:
            current = production[1]
        else:
            break

    return ''.join(result)
```

### Grammar to Finite Automaton conversion (`to_finite_automaton`)

This method implements the standard algorithm for converting a right-linear grammar into an equivalent finite automaton. The states of the automaton are the non-terminals plus a new accepting state X, the start state is S, and the only final state is X. For each production A -> aB, a transition delta(A, a) = B is added, for each production A -> a, a transition delta(A, a) = X is added, directing to the final state.

```python
def to_finite_automaton(self):
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
```

### Finite Automaton class and string validation (`finite_automaton.py`)

The FiniteAutomaton class stores the five standard components: states Q, alphabet Sigma, transition function delta (as a dictionary (state, symbol) to next states), start state q0, and final states F. The transition function uses sets of states just in case it is a NFA and tehre maybe moree than one next state(i don't have this in my variant though, but i tried to make the programs like scalable, i tried different variants and they seem to work with my implementation of Grammar and FA).

The string_belongs_to_language method simulates the automaton on the input string. It just takes current states and for each symbol finds all nest possible states. If the set becomes empty at any point, the string is immediately considered as trash. After processing all symbols, the string is accepted if any of the current states is a final state, in other words it ends with X as should be.

```python
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
```

### Main driver (`main.py`)

The main script instantiates the grammar for Variant 20, generates 5 random valid strings(maybe they should be unique but i am too lazy to do this), converts the grammar to a finite automaton, prints the automaton's components, and then tests 8 strings (4 valid and 4 invalid) to verify the automaton's acceptance behavior.

```python
grammar = Grammar(vn, vt, productions, 'S')

for i in range(5):
    word = grammar.generate_string()
    print(f"  {i + 1}. {word}")

fa = grammar.to_finite_automaton()

for s in test_strings:
    result = fa.string_belongs_to_language(s)
    print(f"  '{s}' -> {'ACCEPTED' if result else 'REJECTED'}")
```


## Conclusions 
In conclusion this was a grea laboratory, i needed to implement a grammar which was somwhat easy, the ineresting part was to work with finite automaton because we coudn't learn about this at the course(thanks to Braga!?), so i read myself the book, had some headaches while trying to understand this properly. I then wrote on a paper an algorithm to transform grammar to FA just so later i found that in book this is already explained(such a great waste of time, but interesting at least). It was also a little pain to make the function string_belongs_to_language because in words easy to say harder in a program.

So, i learned how to work with grammars and FA, implemented them and while implementing i understand even more the actual theory of the last chapters.


## References
Technical University of MoldovaFormal Languages and Finite AutomataGuide for practical lessonsChișinău, 2022