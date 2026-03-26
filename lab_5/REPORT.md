# Lab 5: Chomsky Normal Form

### Course: Formal Languages & Finite Automata
### Author: Rusnac Nichita

----

## Theory
Chomsky Normal Form (CNF) is a standardized form for context-free grammars where each production is either a pair of nonterminals or a single terminal. A grammar in CNF has rules of the form $A \to BC$ or $A \to a$, plus an optional $S \to \epsilon$ when the start symbol can derive the empty string. Normalizing a grammar to CNF makes it easier to apply algorithms like CYK parsing and to prove properties about the language because every derivation is built from the same small set of rule shapes.

The conversion to CNF is not a single step but a pipeline of well-defined transformations. These steps remove special cases and simplify the structure of the grammar without changing the language (except for the possible handling of $\epsilon$ when allowed). The typical pipeline is: eliminate epsilon productions, remove unit productions, remove inaccessible symbols, remove nonproductive symbols, and finally rewrite long right-hand sides into binary rules while replacing terminals inside long rules with helper nonterminals. The algorithm implemented in this lab follows exactly this order.

## Objectives:

* Learn about Chomsky Normal Form and normalization steps.
* Implement an algorithm that transforms a grammar into CNF.
* Ensure the implementation works for arbitrary grammars with the same representation.

## Implementation description

### Grammar representation

The grammar is stored using sets for nonterminals and terminals and a dictionary for productions. Each production right-hand side is represented as a tuple of symbols, which makes it easy to manipulate and compare rules across transformations.

```python
@dataclass
class Grammar:
    vn: Set[str]
    vt: Set[str]
    productions: Dict[str, List[Tuple[str, ...]]]
    start: str
```

The `parse_rhs()` helper accepts either a compact string (like `aB`) or a space-separated form and returns a tuple of symbols. This keeps the input flexible and ensures the normalization code works for any grammar with the same symbol representation.

```python
def parse_rhs(text: str) -> Tuple[str, ...]:
    stripped = text.strip()
    if stripped in ("", EPSILON, "eps", "epsilon"):
        return tuple()
    if " " in stripped:
        return tuple(part for part in stripped.split(" ") if part)
    return tuple(stripped)
```

### Eliminating epsilon productions

The epsilon elimination step first computes the nullable set, then generates all possible alternatives where nullable symbols are either kept or removed. This preserves the language while removing $\epsilon$ rules, except possibly for the start symbol.

```python
if grammar.start in nullable and tuple() not in new_productions[grammar.start]:
    new_productions[grammar.start].append(tuple())
```

The helper `_nullable_expansions` performs the combinational expansion of a right-hand side, which is the key to removing epsilon productions correctly.

```python
def _nullable_expansions(rhs: Tuple[str, ...], nullable: Set[str]) -> Set[Tuple[str, ...]]:
    results: Set[Tuple[str, ...]] = set()
    def backtrack(index: int, current: List[str]) -> None:
        if index == len(rhs):
            results.add(tuple(current))
            return
        symbol = rhs[index]
        if symbol in nullable:
            backtrack(index + 1, current)
        current.append(symbol)
        backtrack(index + 1, current)
        current.pop()
    backtrack(0, [])
    return results
```

### Eliminating unit productions (renaming)

Unit productions are rules like $A \to B$. The algorithm computes the unit closure for every nonterminal, then replaces unit chains with the target non-unit rules. This removes renaming without changing the language.

```python
unit_closure = {nt: _unit_closure(nt, grammar.productions, grammar.vn) for nt in grammar.vn}
```

### Removing inaccessible and nonproductive symbols

Inaccessible symbols are those never reachable from the start symbol. Nonproductive symbols are those that can never derive a terminal string. Both are removed to simplify the grammar and avoid useless rules.

```python
reachable = set([grammar.start])
...
grammar.vn = reachable
grammar.productions = {k: v for k, v in grammar.productions.items() if k in reachable}
```

```python
productive: Set[str] = set()
...
grammar.vn = grammar.vn.intersection(productive)
```

### CNF conversion

The CNF transformation replaces terminals inside long rules with helper nonterminals (like `T_a -> a`) and splits right-hand sides longer than two into a chain of binary rules.

```python
def get_terminal_symbol(term: str) -> str:
    if term not in mapping:
        name = _fresh_nonterminal(f"T_{term}", grammar.vn)
        grammar.vn.add(name)
        new_productions[name] = [(term,)]
        mapping[term] = name
    return mapping[term]
```

```python
while len(symbols) > 2:
    first = symbols.pop(0)
    new_head = _fresh_nonterminal("X", grammar.vn)
    grammar.vn.add(new_head)
    final_productions[current_head].append((first, new_head))
    current_head = new_head
```

### Tests and validation

The lab includes a CNF validation check that enforces the structural rules of CNF: each production must be either $A \to BC$, $A \to a$, or $S \to \epsilon$ (only for the start symbol). The test reports any violations so the output clearly shows whether the normal form is correct.

```python
ok, issues = cnf.validate_cnf()
if ok:
    print("CNF check passed: all productions follow CNF rules.")
else:
    print("CNF check failed:")
```

### Main program

The main runner builds the variant grammar, applies each normalization step, prints intermediate grammars, and then prints the final CNF with validation output. This makes the transformation sequence easy to inspect during the presentation.

```python
no_eps = grammar.eliminate_epsilon()
no_unit = no_eps.eliminate_unit()
no_inacc = no_unit.eliminate_inaccessible()
no_nonprod = no_inacc.eliminate_nonproductive()
cnf = no_nonprod.to_cnf()
```

```python
# Break long right-hand sides into binary rules.
while len(symbols) > 2:
    first = symbols.pop(0)
    new_head = _fresh_nonterminal("X", grammar.vn)
    ...
```

## Conclusions / Screenshots / Results

The implementation follows the required normalization sequence and prints each intermediate grammar, which makes the process transparent and easy to verify. The final output is in Chomsky Normal Form and the validation test confirms that every rule respects CNF structure.

The additional bounded language check provides extra confidence that the transformations preserve the language (within a practical limit). By comparing the sets of strings generated up to a short length, the program shows that the original CFG and the resulting CNF behave the same for all short derivations, which is especially useful for debugging and presentation.

Because the code operates on a general grammar representation and does not hardcode any variant-specific steps, it can be reused for other grammars with the same input format. The pipeline design also makes it easy to extend the project with additional checks, visualization tools, or parsing algorithms such as CYK. Overall, the project delivers a complete and reusable CNF normalization workflow with both structural and behavioral validation.

## References

* Chomsky Normal Form (Wikipedia).
* Course materials and task description.
