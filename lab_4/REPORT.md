# Lab 4: Regular Expressions

### Course: Formal Languages & Finite Automata
### Author: Rusnac Nichita

----

## Theory
Regular expressions are a compact formalism for describing regular languages. A regex is built from literals and operators such as concatenation, alternation, and repetition, and each expression defines a set of strings. This notation is widely used in programming languages, text editors, and formal language theory because it provides a concise way to state complex patterns while remaining mathematically precise.

From the formal languages perspective, every regex corresponds to a finite automaton that accepts the same language. This equivalence is important because it means we can either recognize strings with an automaton or generate strings directly from the regex. The operators used in the task map naturally to language operations: concatenation corresponds to string concatenation, alternation corresponds to union, and repetition corresponds to the Kleene star or bounded repetition. For generation, the idea is to interpret the regex dynamically and create strings that satisfy all rules instead of hardcoding any pattern-specific logic.

## Objectives:

* Explain what regular expressions are and where they are used.
* Implement a generator that builds valid strings from a set of regex patterns.
* Keep repetitions bounded to avoid infinite output and show the processing order (bonus).

## Implementation description

### Tokenizer

The tokenizer converts a regex string into a stream of tokens. It recognizes literals, parentheses, operators, and repetition counts. For the assignment, I also support superscript counts (like 2 or 3) so the regex can be copied directly from the task. Tokens are represented as a small `Token` class with a type and optional value.

```python
class Token:
    def __init__(self, type: str, value: Optional[str] = None):
        self.type = type
        self.value = value
```

This structure is intentionally minimal because the parser only needs the token kind and, for numbers, the token value. Keeping it small makes the tokenizer easy to maintain and reduces the amount of state passed around in later stages.

The main loop scans the pattern character by character and emits tokens for operators, counts, and literals. Digits are treated as literals (so patterns like `(2|3)` work), while superscripts become numeric counts for repetition.

```python
if ch in SUPERSCRIPT_DIGITS:
    digits = []
    while self._current() in SUPERSCRIPT_DIGITS:
        digits.append(SUPERSCRIPT_DIGITS[self._current()])
        self._advance()
    tokens.append(Token("SUP_NUMBER", "".join(digits)))
    continue

if ch.isdigit():
    digits = []
    while self._current() is not None and self._current().isdigit():
        digits.append(self._advance())
    tokens.append(Token("NUMBER", "".join(digits)))
    continue
```

In this block, superscript digits are treated as repetition counts, while normal digits are preserved as literal symbols. This choice allows patterns like `(2|3)` from the task to be parsed as regular literals, and patterns like `Xb2` to be interpreted as repetition. The tokenizer decides this early, so the parser can remain simple.

### Parser (AST construction)

A recursive descent parser builds an abstract syntax tree (AST). The grammar is intentionally minimal: alternation (`|`), concatenation, grouping with parentheses, and repetition operators (`*`, `+`, `?`, `{m,n}`, superscripts). Each parsing step records a short message that can be shown as the bonus “processing order” output.

```python
# expression -> term ( '|' term )*
def _parse_expression(self) -> Node:
    parts = [self._parse_term()]
    while self._current().type == "|":
        self._advance()
        parts.append(self._parse_term())
    if len(parts) == 1:
        return parts[0]
    self.steps.append("Build alternation")
    return Alternation(parts)
```

This function translates the infix `|` operator into an `Alternation` node. The `steps` list is updated here so the output can show when alternation groups were created. Because alternation has lower precedence than concatenation, this method calls `_parse_term()` which groups factors together first.

Concatenation is implicit: a sequence of factors in a term produces a `Concat` node.

```python
# term -> factor factor*
def _parse_term(self) -> Node:
    factors: List[Node] = []
    while self._current().type not in ("|", ")", "EOF"):
        factors.append(self._parse_factor())
    if not factors:
        return Empty()
    if len(factors) == 1:
        return factors[0]
    self.steps.append("Build concatenation")
    return Concat(factors)
```

Concatenation is implicit, so a term keeps reading factors until it reaches a token that ends the term (`|`, `)` or end of file). This mirrors the way regexes are commonly written without explicit concatenation operators.

### Random generation

Each AST node has a `sample()` method that generates one valid string. This is where the random behavior is implemented. Alternation chooses a branch uniformly, repetition chooses a random count between the minimum and a global cap (5), and concatenation merges the sampled parts.

```python
class Alternation(Node):
    def sample(self, max_repeat: int) -> str:
        choice = random.choice(self.options)
        return choice.sample(max_repeat)
```

Random alternation uses `random.choice`, which gives a uniform 50/50 split for two options. For more than two options, the probability is still uniform across all branches. This keeps the sampling logic short and predictable.

```python
class Repeat(Node):
    def sample(self, max_repeat: int) -> str:
        if self.max_times < self.min_times:
            return ""
        cap = min(self.max_times, max_repeat)
        count = random.randint(self.min_times, cap)
        return "".join(self.child.sample(max_repeat) for _ in range(count))
```

This implements the bounded repetition requirement. For `*`, the minimum is 0; for `+`, the minimum is 1; and for explicit ranges the minimum and maximum come from the pattern. The global cap avoids huge strings while still showing variability.

The top-level helper function repeatedly samples strings and keeps unique results, which prevents duplicates when the regex has many overlapping paths.

```python
def generate_random_strings(pattern: str, max_repeat: int = 5, count: int = 20, max_attempts: int = 200):
    ...
    while len(results) < count and attempts < max_attempts:
        value = ast.sample(max_repeat)
        if value in seen:
            continue
        results.append(value)
```

The loop retries sampling until it either collects enough unique strings or reaches a safe attempt limit. This prevents infinite loops in expressions that only generate a few distinct outputs, while still keeping the output diverse.

### Main program

The main script defines the three regexes from the variant, then runs the random generator for each one. It prints the generated strings and the parsing steps.

```python
regexes = [
    "(S|T)(U|V)w*Y+24",
    "L(M|N)O{3}P*Q(2|3)",
    "R*S(T|U|V)W(X|Y|Z){2}",
]

for idx, pattern in enumerate(regexes, start=1):
    print_generation(f"Example {idx}", pattern)
```

* Code snippets from your files are included above with explanations, following the implementation flow: tokenization, parsing, generation, and the main runner.

## Conclusions / Screenshots / Results

The program generates random valid strings for each regex in the variant and remains generic for other patterns that use the same operators. By keeping repetition bounded and using a structured AST, the solution avoids hardcoding and stays easy to extend.

The random sampling approach is especially useful for demonstrations: each run provides different examples while still respecting the regex rules. The internal processing log makes it clear how the regex was parsed and which operations were applied, which is helpful when presenting the lab and explaining the behavior. Because the tokenizer and parser are separate from the generator, the code is modular and can be reused later for tasks like regex validation, exhaustive generation, or conversion to automata.

Overall, the implementation meets the requirements of dynamic interpretation, bounded repetition, and transparent processing. It produces concise, readable output and can be adapted to additional regex operators with minimal changes.

## References

* Course materials and task description.
* Python documentation for basic string handling.
