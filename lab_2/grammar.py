class Grammar:
    def __init__(self, vn, vt, productions, start_symbol):
        self.vn = vn
        self.vt = vt
        self.productions = productions
        self.start_symbol = start_symbol

    def classify(self):
        # Classify the grammar based on Chomsky hierarchy.

        if self._is_type3():
            return "Type 3 (Regular Grammar)"
        if self._is_type2():
            return "Type 2 (Context-Free Grammar)"
        if self._is_type1():
            return "Type 1 (Context-Sensitive Grammar)"
        return "Type 0 (Unrestricted Grammar)"

    def _is_type3(self):
        """
        A regular grammar is either entirely right-linear or entirely left-linear.
        Right-linear: A -> aB | a
        Left-linear:  A -> Ba | a
        """
        has_right_linear = False
        has_left_linear = False

        for lhs, rhs_list in self.productions.items():
            # LHS must be a single non-terminal
            if lhs not in self.vn:
                return False

            for rhs in rhs_list:

                # Single terminal: A -> a
                if len(rhs) == 1:
                    if rhs in self.vt:
                        continue  # valid in both right and left linear
                    else:
                        return False

                # Two symbols
                if len(rhs) == 2:
                    if rhs[0] in self.vt and rhs[1] in self.vn:
                        # A -> aB (right-linear)
                        has_right_linear = True
                    elif rhs[0] in self.vn and rhs[1] in self.vt:
                        # A -> Ba (left-linear)
                        has_left_linear = True
                    else:
                        return False
                    continue

                # Longer productions (extended regular grammar)
                if len(rhs) > 2:
                    # Right-linear: A -> a1a2...anB (terminals then one non-terminal)
                    all_t_then_nt = all(c in self.vt for c in rhs[:-1]) and rhs[-1] in self.vn
                    # Left-linear: A -> Ba1a2...an (one non-terminal then terminals)
                    nt_then_all_t = rhs[0] in self.vn and all(c in self.vt for c in rhs[1:])
                    # All terminals: A -> a1a2...an
                    all_terminals = all(c in self.vt for c in rhs)

                    if all_terminals:
                        continue
                    elif all_t_then_nt:
                        has_right_linear = True
                    elif nt_then_all_t:
                        has_left_linear = True
                    else:
                        return False

        # Cannot mix right-linear and left-linear productions
        if has_right_linear and has_left_linear:
            return False

        return True

    def _is_type2(self):
        # All productions must have a single non-terminal on the LHS.
        for lhs in self.productions:
            if lhs not in self.vn:
                return False
        return True

    def _is_type1(self):
        # For all productions α -> β: |α| <= |β| and ε shoudn't appear on the rhs
        for lhs, rhs_list in self.productions.items():
            for rhs in rhs_list:
                if rhs == '' or rhs == 'ε':
                    return False
                elif len(lhs) > len(rhs):
                    return False
        return True

    def __str__(self):
        lines = [
            f"Grammar:",
            f"  Non-terminals (V_N): {sorted(self.vn)}",
            f"  Terminals (V_T): {sorted(self.vt)}",
            f"  Start symbol: {self.start_symbol}",
            f"  Productions:",
        ]
        for lhs in sorted(self.productions):
            rhs_strs = [rhs if rhs else 'ε' for rhs in self.productions[lhs]]
            lines.append(f"    {lhs} → {' | '.join(rhs_strs)}")
        return '\n'.join(lines)
