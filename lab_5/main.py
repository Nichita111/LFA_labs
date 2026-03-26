from grammar_cnf import EPSILON, Grammar, parse_rhs


def build_productions(raw):
    productions = {}
    for head, rhs_list in raw.items():
        productions[head] = [parse_rhs(rhs) for rhs in rhs_list]
    return productions


def main() -> None:
    print("Lab 5: Chomsky Normal Form")
    print("Variant 20")

    vn = {"S", "A", "B", "C", "D"}
    vt = {"a", "b"}

    raw_productions = {
        "S": ["aB", "bA", "A"],
        "A": ["B", "Sa", "bBA", "b"],
        "B": ["b", "bS", "aD", EPSILON],
        "D": ["AA"],
        "C": ["Ba"],
    }

    grammar = Grammar(vn, vt, build_productions(raw_productions), "S")

    print("\nOriginal Grammar")
    print(grammar)

    no_eps = grammar.eliminate_epsilon()
    print("\nAfter eliminating epsilon productions")
    print(no_eps)

    no_unit = no_eps.eliminate_unit()
    print("\nAfter eliminating renaming (unit productions)")
    print(no_unit)

    no_inacc = no_unit.eliminate_inaccessible()
    print("\nAfter eliminating inaccessible symbols")
    print(no_inacc)

    no_nonprod = no_inacc.eliminate_nonproductive()
    print("\nAfter eliminating nonproductive symbols")
    print(no_nonprod)

    cnf = no_nonprod.to_cnf()
    print("\nChomsky Normal Form")
    print(cnf)

    ok, issues = cnf.validate_cnf()
    print("\nCNF validation")
    if ok:
        print("CNF check passed: all productions follow CNF rules.")
    else:
        print("CNF check failed:")
        for issue in issues:
            print(f"  - {issue}")


if __name__ == "__main__":
    main()
