import random
from dataclasses import dataclass
from typing import List, Optional, Tuple


class RegexError(Exception):
    pass


# Simple token representation.
@dataclass
class Token:
    type: str
    value: Optional[str] = None


SUPERSCRIPT_DIGITS = {
    "\u2070": "0",
    "\u00b9": "1",
    "\u00b2": "2",
    "\u00b3": "3",
    "\u2074": "4",
    "\u2075": "5",
    "\u2076": "6",
    "\u2077": "7",
    "\u2078": "8",
    "\u2079": "9",
}


class Tokenizer:
    def __init__(self, source: str):
        self.source = source
        self.pos = 0

    def _current(self) -> Optional[str]:
        if self.pos < len(self.source):
            return self.source[self.pos]
        return None

    def _advance(self) -> Optional[str]:
        ch = self._current()
        self.pos += 1
        return ch

    def tokenize(self) -> List[Token]:
        tokens: List[Token] = []
        while self._current() is not None:
            ch = self._current()
            if ch.isspace():
                self._advance()
                continue
            if ch == "\\":
                self._advance()
                esc = self._current()
                if esc is None:
                    raise RegexError("Dangling escape at end of pattern")
                tokens.append(Token("LITERAL", esc))
                self._advance()
                continue
            if ch in "()|*+?{} ,":
                if ch == " ":
                    self._advance()
                    continue
                if ch == ",":
                    tokens.append(Token("COMMA", ch))
                elif ch == "{":
                    tokens.append(Token("LBRACE", ch))
                elif ch == "}":
                    tokens.append(Token("RBRACE", ch))
                else:
                    tokens.append(Token(ch, ch))
                self._advance()
                continue
            # Superscript counts like nb2 or nb3.
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
            # Default: treat as literal.
            tokens.append(Token("LITERAL", ch))
            self._advance()
        tokens.append(Token("EOF"))
        return tokens


# AST node definitions.
class Node:
    def generate(self, max_repeat: int, max_results: int) -> List[str]:
        raise NotImplementedError

    def sample(self, max_repeat: int) -> str:
        raise NotImplementedError


@dataclass
class Empty(Node):
    def generate(self, max_repeat: int, max_results: int) -> List[str]:
        return [""]

    def sample(self, max_repeat: int) -> str:
        return ""


@dataclass
class Literal(Node):
    value: str

    def generate(self, max_repeat: int, max_results: int) -> List[str]:
        return [self.value]

    def sample(self, max_repeat: int) -> str:
        return self.value


@dataclass
class Concat(Node):
    parts: List[Node]

    def generate(self, max_repeat: int, max_results: int) -> List[str]:
        results = [""]
        for part in self.parts:
            next_values = part.generate(max_repeat, max_results)
            results = _concat_lists(results, next_values, max_results)
            if len(results) >= max_results:
                return results[:max_results]
        return results

    def sample(self, max_repeat: int) -> str:
        return "".join(part.sample(max_repeat) for part in self.parts)


@dataclass
class Alternation(Node):
    options: List[Node]

    def generate(self, max_repeat: int, max_results: int) -> List[str]:
        seen = set()
        out: List[str] = []
        for opt in self.options:
            for value in opt.generate(max_repeat, max_results):
                if value not in seen:
                    seen.add(value)
                    out.append(value)
                if len(out) >= max_results:
                    return out[:max_results]
        return out

    def sample(self, max_repeat: int) -> str:
        choice = random.choice(self.options)
        return choice.sample(max_repeat)


@dataclass
class Repeat(Node):
    child: Node
    min_times: int
    max_times: int

    def generate(self, max_repeat: int, max_results: int) -> List[str]:
        max_times = self.max_times
        if max_times < self.min_times:
            return []
        base = self.child.generate(max_repeat, max_results)
        results: List[str] = []
        for count in range(self.min_times, max_times + 1):
            if count == 0:
                results.append("")
                if len(results) >= max_results:
                    return results[:max_results]
                continue
            current = [""]
            for _ in range(count):
                current = _concat_lists(current, base, max_results)
                if len(current) >= max_results:
                    current = current[:max_results]
                    break
            for value in current:
                results.append(value)
                if len(results) >= max_results:
                    return results[:max_results]
        return results

    def sample(self, max_repeat: int) -> str:
        if self.max_times < self.min_times:
            return ""
        cap = min(self.max_times, max_repeat)
        count = random.randint(self.min_times, cap)
        return "".join(self.child.sample(max_repeat) for _ in range(count))


class Parser:
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.pos = 0
        self.steps: List[str] = []

    def _current(self) -> Token:
        return self.tokens[self.pos]

    def _advance(self) -> Token:
        tok = self._current()
        self.pos += 1
        return tok

    def _expect(self, token_type: str) -> Token:
        tok = self._current()
        if tok.type != token_type:
            raise RegexError(f"Expected {token_type}, got {tok.type}")
        self.pos += 1
        return tok

    def parse(self) -> Node:
        node = self._parse_expression()
        if self._current().type != "EOF":
            raise RegexError(f"Unexpected token: {self._current().type}")
        return node

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

    # factor -> base ( '*' | '+' | '?' | '{m,n}' | superscript )?
    def _parse_factor(self) -> Node:
        base = self._parse_base()
        tok = self._current()
        if tok.type in ("*", "+", "?"):
            self._advance()
            if tok.type == "*":
                self.steps.append("Apply repeat *")
                return Repeat(base, 0, self._repeat_cap())
            if tok.type == "+":
                self.steps.append("Apply repeat +")
                return Repeat(base, 1, self._repeat_cap())
            self.steps.append("Apply repeat ?")
            return Repeat(base, 0, 1)
        if tok.type == "LBRACE":
            repeat = self._parse_brace_repeat()
            self.steps.append(f"Apply repeat {{{repeat[0]},{repeat[1]}}}")
            return Repeat(base, repeat[0], repeat[1])
        if tok.type == "SUP_NUMBER":
            count = int(self._advance().value)
            self.steps.append(f"Apply repeat {{{count}}}")
            return Repeat(base, count, count)
        return base

    def _parse_brace_repeat(self) -> Tuple[int, int]:
        self._expect("LBRACE")
        if self._current().type != "NUMBER":
            raise RegexError("Expected number in repeat")
        min_times = int(self._advance().value)
        max_times = min_times
        if self._current().type == "COMMA":
            self._advance()
            if self._current().type == "NUMBER":
                max_times = int(self._advance().value)
            else:
                max_times = self._repeat_cap()
        self._expect("RBRACE")
        return min_times, max_times

    def _parse_base(self) -> Node:
        tok = self._current()
        if tok.type == "(":
            self._advance()
            node = self._parse_expression()
            self._expect(")")
            self.steps.append("Close group")
            return node
        if tok.type == "LITERAL":
            self._advance()
            self.steps.append(f"Read literal '{tok.value}'")
            return Literal(tok.value)
        if tok.type == "NUMBER":
            self._advance()
            self.steps.append(f"Read literal '{tok.value}'")
            return Literal(tok.value)
        raise RegexError(f"Unexpected token: {tok.type}")

    def _repeat_cap(self) -> int:
        return 5


def _concat_lists(left: List[str], right: List[str], max_results: int) -> List[str]:
    out: List[str] = []
    for a in left:
        for b in right:
            out.append(a + b)
            if len(out) >= max_results:
                return out[:max_results]
    return out


def generate_strings(pattern: str, max_repeat: int = 5, max_results: int = 30) -> Tuple[List[str], List[str]]:
    tokenizer = Tokenizer(pattern)
    tokens = tokenizer.tokenize()
    parser = Parser(tokens)
    # Override repeat cap for this run.
    def _cap_override(self) -> int:
        return max_repeat
    parser._repeat_cap = _cap_override.__get__(parser, Parser)

    ast = parser.parse()

    results = ast.generate(max_repeat, max_results)
    return results, parser.steps


def generate_random_strings(
    pattern: str,
    max_repeat: int = 5,
    count: int = 20,
    max_attempts: int = 200,
) -> Tuple[List[str], List[str]]:
    tokenizer = Tokenizer(pattern)
    tokens = tokenizer.tokenize()
    parser = Parser(tokens)

    def _cap_override(self) -> int:
        return max_repeat
    parser._repeat_cap = _cap_override.__get__(parser, Parser)

    ast = parser.parse()
    results: List[str] = []
    seen = set()
    attempts = 0
    while len(results) < count and attempts < max_attempts:
        value = ast.sample(max_repeat)
        attempts += 1
        if value in seen:
            continue
        seen.add(value)
        results.append(value)
    return results, parser.steps
