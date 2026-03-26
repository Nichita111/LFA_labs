from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, List, Set, Tuple


EPSILON = "eps"


def parse_rhs(text: str) -> Tuple[str, ...]:
    stripped = text.strip()
    if stripped in ("", EPSILON, "eps", "epsilon"):
        return tuple()
    if " " in stripped:
        return tuple(part for part in stripped.split(" ") if part)
    return tuple(stripped)


@dataclass
class Grammar:
    vn: Set[str]
    vt: Set[str]
    productions: Dict[str, List[Tuple[str, ...]]]
    start: str

    def copy(self) -> "Grammar":
        return Grammar(
            set(self.vn),
            set(self.vt),
            {k: list(v) for k, v in self.productions.items()},
            self.start,
        )

    def __str__(self) -> str:
        lines = []
        lines.append(f"V_N = {sorted(self.vn)}")
        lines.append(f"V_T = {sorted(self.vt)}")
        lines.append("P = {")
        for head in sorted(self.productions):
            rhs_list = [self._format_rhs(rhs) for rhs in self.productions[head]]
            joined = " | ".join(rhs_list) if rhs_list else EPSILON
            lines.append(f"  {head} -> {joined}")
        lines.append("}")
        return "\n".join(lines)

    def _format_rhs(self, rhs: Tuple[str, ...]) -> str:
        if not rhs:
            return EPSILON
        return "".join(rhs)

    def eliminate_epsilon(self) -> "Grammar":
        grammar = self.copy()
        nullable = set()
        changed = True

        while changed:
            changed = False
            for head, rhs_list in grammar.productions.items():
                if head in nullable:
                    continue
                for rhs in rhs_list:
                    if not rhs:
                        nullable.add(head)
                        changed = True
                        break
                    if all(symbol in nullable for symbol in rhs):
                        nullable.add(head)
                        changed = True
                        break

        new_productions: Dict[str, List[Tuple[str, ...]]] = {k: [] for k in grammar.vn}
        for head, rhs_list in grammar.productions.items():
            for rhs in rhs_list:
                if not rhs:
                    continue
                options = _nullable_expansions(rhs, nullable)
                for option in options:
                    if option or head == grammar.start:
                        if option not in new_productions[head]:
                            new_productions[head].append(option)

        if grammar.start in nullable and tuple() not in new_productions[grammar.start]:
            new_productions[grammar.start].append(tuple())

        grammar.productions = new_productions
        return grammar

    def eliminate_unit(self) -> "Grammar":
        grammar = self.copy()
        unit_closure = {nt: _unit_closure(nt, grammar.productions, grammar.vn) for nt in grammar.vn}

        new_productions: Dict[str, List[Tuple[str, ...]]] = {k: [] for k in grammar.vn}
        for head in grammar.vn:
            for target in unit_closure[head]:
                for rhs in grammar.productions.get(target, []):
                    if len(rhs) == 1 and rhs[0] in grammar.vn:
                        continue
                    if rhs not in new_productions[head]:
                        new_productions[head].append(rhs)

        grammar.productions = new_productions
        return grammar

    def eliminate_inaccessible(self) -> "Grammar":
        grammar = self.copy()
        reachable = set([grammar.start])
        changed = True

        while changed:
            changed = False
            for head in list(reachable):
                for rhs in grammar.productions.get(head, []):
                    for symbol in rhs:
                        if symbol in grammar.vn and symbol not in reachable:
                            reachable.add(symbol)
                            changed = True

        grammar.vn = reachable
        grammar.productions = {k: v for k, v in grammar.productions.items() if k in reachable}
        return grammar

    def eliminate_nonproductive(self) -> "Grammar":
        grammar = self.copy()
        productive: Set[str] = set()
        changed = True

        while changed:
            changed = False
            for head, rhs_list in grammar.productions.items():
                if head in productive:
                    continue
                for rhs in rhs_list:
                    if all((symbol in grammar.vt) or (symbol in productive) for symbol in rhs):
                        productive.add(head)
                        changed = True
                        break

        grammar.vn = grammar.vn.intersection(productive)
        new_productions: Dict[str, List[Tuple[str, ...]]] = {}
        for head in grammar.vn:
            filtered = []
            for rhs in grammar.productions.get(head, []):
                if all((symbol in grammar.vt) or (symbol in grammar.vn) for symbol in rhs):
                    filtered.append(rhs)
            new_productions[head] = filtered

        grammar.productions = new_productions
        return grammar

    def to_cnf(self) -> "Grammar":
        grammar = self.copy()
        original_productions = {k: list(v) for k, v in grammar.productions.items()}
        mapping: Dict[str, str] = {}
        new_productions: Dict[str, List[Tuple[str, ...]]] = {k: [] for k in grammar.vn}

        def get_terminal_symbol(term: str) -> str:
            if term not in mapping:
                name = _fresh_nonterminal(f"T_{term}", grammar.vn)
                grammar.vn.add(name)
                new_productions[name] = [(term,)]
                mapping[term] = name
            return mapping[term]

        for head, rhs_list in original_productions.items():
            for rhs in rhs_list:
                if len(rhs) <= 1:
                    new_productions.setdefault(head, []).append(rhs)
                    continue
                replaced = []
                for symbol in rhs:
                    if symbol in grammar.vt:
                        replaced.append(get_terminal_symbol(symbol))
                    else:
                        replaced.append(symbol)
                new_productions.setdefault(head, []).append(tuple(replaced))

        final_productions: Dict[str, List[Tuple[str, ...]]] = {k: [] for k in grammar.vn}
        pair_map: Dict[Tuple[str, str], str] = {}

        def get_pair_symbol(pair: Tuple[str, str]) -> str:
            if pair in pair_map:
                return pair_map[pair]
            name = _fresh_nonterminal("X", grammar.vn)
            grammar.vn.add(name)
            pair_map[pair] = name
            final_productions.setdefault(name, [])
            if pair not in final_productions[name]:
                final_productions[name].append(pair)
            return name
        for head, rhs_list in list(new_productions.items()):
            for rhs in rhs_list:
                if len(rhs) <= 2:
                    if rhs not in final_productions.get(head, []):
                        final_productions.setdefault(head, []).append(rhs)
                    continue
                current_head = head
                symbols = list(rhs)
                while len(symbols) > 2:
                    first = symbols.pop(0)
                    if len(symbols) == 2:
                        pair_nt = get_pair_symbol((symbols[0], symbols[1]))
                        final_productions.setdefault(current_head, [])
                        final_productions[current_head].append((first, pair_nt))
                        symbols = []
                        break
                    new_head = _fresh_nonterminal("X", grammar.vn)
                    grammar.vn.add(new_head)
                    final_productions.setdefault(current_head, [])
                    final_productions[current_head].append((first, new_head))
                    current_head = new_head
                if len(symbols) == 2:
                    final_productions.setdefault(current_head, [])
                    final_productions[current_head].append(tuple(symbols))

        grammar.productions = final_productions
        return grammar

    def validate_cnf(self) -> Tuple[bool, List[str]]:
        issues: List[str] = []
        for head, rhs_list in self.productions.items():
            if head not in self.vn:
                issues.append(f"Nonterminal {head} is not in V_N")
            for rhs in rhs_list:
                for symbol in rhs:
                    if symbol not in self.vn and symbol not in self.vt:
                        issues.append(f"Unknown symbol '{symbol}' in {head} -> {self._format_rhs(rhs)}")

                if len(rhs) == 0:
                    if head != self.start:
                        issues.append(f"Epsilon production not allowed: {head} -> {EPSILON}")
                    continue

                if len(rhs) == 1:
                    if rhs[0] not in self.vt:
                        issues.append(f"Unit production not in CNF: {head} -> {self._format_rhs(rhs)}")
                    continue

                if len(rhs) == 2:
                    if rhs[0] not in self.vn or rhs[1] not in self.vn:
                        issues.append(f"Binary production must be nonterminals: {head} -> {self._format_rhs(rhs)}")
                    continue

                issues.append(f"Production too long for CNF: {head} -> {self._format_rhs(rhs)}")

        return len(issues) == 0, issues


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


def _unit_closure(start: str, productions: Dict[str, List[Tuple[str, ...]]], vn: Set[str]) -> Set[str]:
    closure = set([start])
    stack = [start]
    while stack:
        head = stack.pop()
        for rhs in productions.get(head, []):
            if len(rhs) == 1 and rhs[0] in vn and rhs[0] not in closure:
                closure.add(rhs[0])
                stack.append(rhs[0])
    return closure


def _fresh_nonterminal(prefix: str, vn: Set[str]) -> str:
    if prefix not in vn:
        return prefix
    idx = 1
    while f"{prefix}{idx}" in vn:
        idx += 1
    return f"{prefix}{idx}"
