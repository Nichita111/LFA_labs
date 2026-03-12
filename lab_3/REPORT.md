# Lexer & Scanner

### Course: Formal Languages & Finite Automata
### Author: Rusnac Nichita

----

## Theory

Lexical analysis (or scanning) is the first phase of a compiler or interpreter. A **lexer** (also called a tokenizer or scanner) reads a raw string of characters and converts it into a sequence of **tokens** — meaningful units that the next stages of the compiler can work with. Each token has a **type** (the category, e.g. keyword, identifier, number) and a **value** (the actual text, called a lexeme).

For example, given the input `SELECT name FROM users;`, a lexer produces tokens like `(SELECT, "SELECT")`, `(IDENTIFIER, "name")`, `(FROM, "FROM")`, `(IDENTIFIER, "users")`, `(SEMICOLON, ";")`.

The lexer typically works by scanning the input character by character, applying pattern-matching rules to recognize different token types. Whitespace and comments are usually consumed but not turned into tokens. When the lexer encounters a character it cannot match, it raises an error.

Key concepts:
- **Lexeme**: The actual substring from the source (e.g. `"SELECT"`, `"3.85"`).
- **Token**: A pair of (type, lexeme) with optional metadata like line/column position.
- **Keywords**: Reserved words that have special meaning (e.g. `SELECT`, `WHERE`).
- **Identifiers**: User-defined names for tables, columns, etc.


## Objectives:

* Understand what lexical analysis is.
* Get familiar with the inner workings of a lexer/scanner/tokenizer.
* Implement a sample lexer and show how it works.


## Implementation description

### Choice of Language to Lex

Instead of a simple calculator, I chose to implement a lexer for a **mini SQL-like query language**. This is more interesting because SQL has a richer set of token types: keywords (`SELECT`, `FROM`, `WHERE`, `JOIN`, etc.), identifiers, string literals, numeric literals (both integers and floats), comparison and arithmetic operators, punctuation, and comments.

### Token Types

All token types are defined using a Python `Enum`. They are grouped into categories: SQL keywords, literals, identifiers, operators, punctuation, and a special `EOF` marker.

```python
class TokenType(Enum):
    # Keywords
    SELECT = auto()
    FROM = auto()
    WHERE = auto()
    INSERT = auto()
    INTO = auto()
    VALUES = auto()
    UPDATE = auto()
    SET = auto()
    DELETE = auto()
    CREATE = auto()
    TABLE = auto()
    DROP = auto()
    JOIN = auto()
    ON = auto()
    ORDER = auto()
    BY = auto()
    ASC = auto()
    DESC = auto()
    LIMIT = auto()
    AND = auto()
    OR = auto()
    NOT = auto()
    NULL = auto()

    # Literals
    INTEGER = auto()
    FLOAT = auto()
    STRING = auto()

    # Identifiers
    IDENTIFIER = auto()

    # Operators
    EQUALS = auto()         # =
    NOT_EQUALS = auto()     # !=
    LESS = auto()           # <
    GREATER = auto()        # >
    LESS_EQUAL = auto()     # <=
    GREATER_EQUAL = auto()  # >=
    PLUS = auto()           # +
    MINUS = auto()          # -
    STAR = auto()           # *
    SLASH = auto()          # /

    # Punctuation
    COMMA = auto()
    SEMICOLON = auto()
    LPAREN = auto()
    RPAREN = auto()
    DOT = auto()

    # Special
    EOF = auto()
```

Keywords are automatically mapped from their enum names into a lookup dictionary using a dictionary comprehension, so any word read from the input is compared against this map to decide whether it is a keyword or an identifier.

```python
KEYWORDS = {t.name: t for t in TokenType if t.value <= TokenType.NULL.value}
```

---

### The Token Class

Each `Token` stores its type, its text value, and the line/column where it appeared. The `__repr__` method provides a readable debug output.

```python
class Token:
    def __init__(self, type: TokenType, value: str, line: int, column: int):
        self.type = type
        self.value = value
        self.line = line
        self.column = column

    def __repr__(self):
        return f"Token({self.type.name}, {self.value!r}, line={self.line}, col={self.column})"
```

---

### The Lexer Class

The `Lexer` takes a source string and exposes a `tokenize()` method that returns the full list of tokens. Internally it maintains a position pointer, a line counter, and a column counter.

**Core helpers:**
- `_current()` / `_peek()` — look at the current or next character without consuming.
- `_advance()` — consume the current character and update line/column tracking.

**Scanning methods for complex tokens:**

Numeric literals (integers and floats) are read digit by digit. If a dot followed by more digits is found, the token becomes a `FLOAT`:

```python
def _read_number(self):
    start_col = self.column
    result = ''
    is_float = False
    while self._current() is not None and self._current().isdigit():
        result += self._advance()
    if self._current() == '.' and self._peek() is not None and self._peek().isdigit():
        is_float = True
        result += self._advance()  # consume '.'
        while self._current() is not None and self._current().isdigit():
            result += self._advance()
    token_type = TokenType.FLOAT if is_float else TokenType.INTEGER
    return Token(token_type, result, self.line, start_col)
```

String literals are enclosed in single or double quotes. A `LexerError` is raised if the string is not properly terminated:

```python
def _read_string(self):
    start_col = self.column
    quote_char = self._advance()
    result = ''
    while self._current() is not None and self._current() != quote_char:
        if self._current() == '\n':
            raise LexerError("Unterminated string (newline in string)", self.line, self.column)
        result += self._advance()
    if self._current() is None:
        raise LexerError("Unterminated string", self.line, self.column)
    self._advance()  # consume closing quote
    return Token(TokenType.STRING, result, self.line, start_col)
```

Identifiers and keywords share the same reading logic. After reading the word, its uppercase form is checked against the keywords map:

```python
def _read_identifier_or_keyword(self):
    start_col = self.column
    result = ''
    while self._current() is not None and (self._current().isalnum() or self._current() == '_'):
        result += self._advance()
    upper = result.upper()
    if upper in KEYWORDS:
        return Token(KEYWORDS[upper], result, self.line, start_col)
    return Token(TokenType.IDENTIFIER, result, self.line, start_col)
```

---

### The Main Tokenize Loop

The `tokenize()` method loops through the input, dispatching to the appropriate handler based on the current character. It skips whitespace and `--` comments, then tries to match numbers, strings, identifiers/keywords, two-character operators (`!=`, `<=`, `>=`), single-character operators, and punctuation. If none match, it raises a `LexerError`.

```python
def tokenize(self):
    tokens = []
    while self._current() is not None:
        if self._current() in ' \t\r\n':
            self._skip_whitespace()
            continue
        if self._current() == '-' and self._peek() == '-':
            self._skip_comment()
            continue
        if self._current().isdigit():
            tokens.append(self._read_number())
            continue
        if self._current() in ("'", '"'):
            tokens.append(self._read_string())
            continue
        if self._current().isalpha() or self._current() == '_':
            tokens.append(self._read_identifier_or_keyword())
            continue
        # ... operators and punctuation handling ...
        bad = self._current()
        raise LexerError(f"Unexpected character: {bad!r}", self.line, self.column)
    tokens.append(Token(TokenType.EOF, '', self.line, self.column))
    return tokens
```

---

### Error Handling

The `LexerError` class includes the line and column of the problematic character, making it easy to locate errors in the input:

```python
class LexerError(Exception):
    def __init__(self, message, line, column):
        super().__init__(f"Lexer error at line {line}, col {column}: {message}")
```

## Conclusions / Screenshots / Results

I implemented a lexer for a mini SQL-like query language. The lexer correctly handles:

- **24 SQL keywords** (SELECT, FROM, WHERE, INSERT, UPDATE, DELETE, CREATE, JOIN, etc.)
- **Identifiers** (table and column names, including those with underscores)
- **Integer and float literals** (e.g. `21`, `3.85`, `5000.50`)
- **String literals** in single or double quotes (e.g. `'Nichita'`, `'completed'`)
- **Comparison operators** (`=`, `!=`, `<`, `>`, `<=`, `>=`)
- **Arithmetic operators** (`+`, `-`, `*`, `/`)
- **Punctuation** (`,`, `;`, `(`, `)`, `.`)
- **Single-line comments** (`-- ...`)
- **Line and column tracking** for every token
- **Error reporting** with precise location for unexpected characters

Below is a sample of the output showing how various SQL queries are tokenized:

**Simple SELECT:**
```
Input: SELECT name, age FROM users WHERE age >= 18;
  Token(SELECT, 'SELECT', line=1, col=1)
  Token(IDENTIFIER, 'name', line=1, col=8)
  Token(COMMA, ',', line=1, col=12)
  Token(IDENTIFIER, 'age', line=1, col=14)
  Token(FROM, 'FROM', line=1, col=18)
  Token(IDENTIFIER, 'users', line=1, col=23)
  Token(WHERE, 'WHERE', line=1, col=29)
  Token(IDENTIFIER, 'age', line=1, col=35)
  Token(GREATER_EQUAL, '>=', line=1, col=39)
  Token(INTEGER, '18', line=1, col=42)
  Token(SEMICOLON, ';', line=1, col=44)
  Token(EOF, '', line=1, col=45)
```

**INSERT with mixed types (string, integer, float):**
```
Input: INSERT INTO students VALUES ('Nichita', 21, 3.85);
  Token(INSERT, 'INSERT', line=1, col=1)
  Token(INTO, 'INTO', line=1, col=8)
  Token(IDENTIFIER, 'students', line=1, col=13)
  Token(VALUES, 'VALUES', line=1, col=22)
  Token(LPAREN, '(', line=1, col=29)
  Token(STRING, 'Nichita', line=1, col=30)
  Token(COMMA, ',', line=1, col=39)
  Token(INTEGER, '21', line=1, col=41)
  Token(COMMA, ',', line=1, col=43)
  Token(FLOAT, '3.85', line=1, col=45)
  Token(RPAREN, ')', line=1, col=49)
  Token(SEMICOLON, ';', line=1, col=50)
  Token(EOF, '', line=1, col=51)
```

**Error handling (unknown character `@`):**
```
Input: SELECT name FROM users WHERE name = @invalid;
  ERROR: Lexer error at line 1, col 37: Unexpected character: '@'
```

The lexer correctly distinguishes keywords from identifiers (case-insensitive keyword matching), handles multi-character operators like `>=` and `!=`, skips comments while preserving correct line tracking, and provides clear error messages with position information.

## References

[1] [A sample of a lexer implementation](https://llvm.org/docs/tutorial/MyFirstLanguageFrontend/LangImpl01.html)

[2] [Lexical analysis](https://en.wikipedia.org/wiki/Lexical_analysis)
