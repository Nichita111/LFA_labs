from regex_generator import generate_random_strings


def print_generation(label: str, pattern: str, max_repeat: int = 5, count: int = 20) -> None:
    print(f"\n{label}")
    print(f"Regex: {pattern}")

    results, steps = generate_random_strings(pattern, max_repeat=max_repeat, count=count)
    print("Randomly generated strings:")
    for value in results:
        print(f"  {value}")

    print("\nProcessing steps (bonus):")
    for step in steps:
        print(f"  - {step}")


def main() -> None:
    print("Lab 4: Regular Expressions")
    print("Variant 4")

    regexes = [
        "(S|T)(U|V)w*Y+24",
        "L(M|N)O{3}P*Q(2|3)",
        "R*S(T|U|V)W(X|Y|Z){2}",
    ]

    for idx, pattern in enumerate(regexes, start=1):
        print_generation(f"Example {idx}", pattern)


if __name__ == "__main__":
    main()
