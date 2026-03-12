from lexer import Lexer, LexerError


def print_tokens(label, source):
    # Tokenize and print the results for a given SQL query.
    print(f"\n {label}")
    print(f"\n Input: {source}")
    print("\n")

    try:
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        for token in tokens:
            print(f"  {token}")
    except LexerError as e:
        print(f"  ERROR: {e}")


def main():
    print("  Lab 3: Lexer & Scanner")
    print("  Mini SQL-like Query Language Lexer")

    # 1. Simple SELECT
    print_tokens(
        "1. Simple SELECT query",
        "SELECT name, age FROM users WHERE age >= 18;"
    )

    # 2. SELECT with ORDER BY and LIMIT
    print_tokens(
        "2. SELECT with ORDER BY and LIMIT",
        "SELECT * FROM products ORDER BY price DESC LIMIT 10;"
    )

    # 3. INSERT statement
    print_tokens(
        "3. INSERT statement",
        "INSERT INTO students VALUES ('Nichita', 21, 3.85);"
    )

    # 4. UPDATE with multiple conditions
    print_tokens(
        "4. UPDATE with conditions",
        "UPDATE employees SET salary = 5000.50 WHERE dept = 'IT' AND years > 3;"
    )

    # 5. DELETE statement
    print_tokens(
        "5. DELETE statement",
        "DELETE FROM orders WHERE status != 'completed';"
    )

    # 6. CREATE TABLE
    print_tokens(
        "6. CREATE TABLE",
        "CREATE TABLE grades (student_id, course, grade);"
    )

    # 7. Query with comment
    print_tokens(
        "7. Query with a comment",
        "SELECT id FROM logs -- this filters active logs\nWHERE active = 1;"
    )

    # 8. JOIN query
    print_tokens(
        "8. JOIN query",
        "SELECT u.name, o.total FROM users u JOIN orders o ON u.id = o.user_id;"
    )

    # 9. Arithmetic in SELECT
    print_tokens(
        "9. Arithmetic expressions",
        "SELECT price * quantity - discount FROM cart;"
    )

    # 10. Error case: unexpected character
    print_tokens(
        "10. Error case — unexpected character",
        "SELECT name FROM users WHERE name = @invalid;"
    )


if __name__ == '__main__':
    main()
