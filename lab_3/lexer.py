from enum import Enum, auto


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
    COMMA = auto()          # ,
    SEMICOLON = auto()      # ;
    LPAREN = auto()         # (
    RPAREN = auto()         # )
    DOT = auto()            # .

    # Special
    EOF = auto()


class Token:
    def __init__(self, type: TokenType, value: str, line: int, column: int):
        self.type = type
        self.value = value
        self.line = line
        self.column = column

    def __repr__(self):
        return f"Token({self.type.name}, {self.value!r}, line={self.line}, col={self.column})"


# Map keyword strings to their token types
KEYWORDS = {t.name: t for t in TokenType if t.value <= TokenType.NULL.value}

# Single-character tokens
SINGLE_CHAR_TOKENS = {
    '+': TokenType.PLUS,
    '-': TokenType.MINUS,
    '*': TokenType.STAR,
    '/': TokenType.SLASH,
    ',': TokenType.COMMA,
    ';': TokenType.SEMICOLON,
    '(': TokenType.LPAREN,
    ')': TokenType.RPAREN,
    '.': TokenType.DOT,
}


class LexerError(Exception):
    def __init__(self, message, line, column):
        super().__init__(f"Lexer error at line {line}, col {column}: {message}")
        self.line = line
        self.column = column


class Lexer:
    def __init__(self, source: str):
        self.source = source
        self.pos = 0
        self.line = 1
        self.column = 1

    def _current(self):
        # Return current character or None if at end
        if self.pos < len(self.source):
            return self.source[self.pos]
        return None

    def _peek(self):
        # Return next character without consuming it
        if self.pos + 1 < len(self.source):
            return self.source[self.pos + 1]
        return None

    def _advance(self):
        # Move to the next character, tracking line and column
        ch = self.source[self.pos]
        self.pos += 1
        if ch == '\n':
            self.line += 1
            self.column = 1
        else:
            self.column += 1
        return ch

    def _skip_whitespace(self):
        while self._current() is not None and self._current() in ' \t\r\n':
            self._advance()

    def _skip_comment(self):
        # Skip single-line comments starting with --
        if self._current() == '-' and self._peek() == '-':
            while self._current() is not None and self._current() != '\n':
                self._advance()

    def _read_number(self):
        # Read an integer or float literal
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

    def _read_string(self):
        # Read a string literal enclosed in single quotes
        start_col = self.column
        quote_char = self._advance()  # consume opening quote
        result = ''

        while self._current() is not None and self._current() != quote_char:
            if self._current() == '\n':
                raise LexerError("Unterminated string (newline in string)", self.line, self.column)
            result += self._advance()

        if self._current() is None:
            raise LexerError("Unterminated string", self.line, self.column)

        self._advance()  # consume closing quote
        return Token(TokenType.STRING, result, self.line, start_col)

    def _read_identifier_or_keyword(self):
        # Read an identifier or keyword
        start_col = self.column
        result = ''

        while self._current() is not None and (self._current().isalnum() or self._current() == '_'):
            result += self._advance()

        upper = result.upper()
        if upper in KEYWORDS:
            return Token(KEYWORDS[upper], result, self.line, start_col)

        return Token(TokenType.IDENTIFIER, result, self.line, start_col)

    def tokenize(self):
        # Tokenize the entire source string and return a list of tokens
        tokens = []

        while self._current() is not None:
            # Skip whitespace
            if self._current() in ' \t\r\n':
                self._skip_whitespace()
                continue

            # Skip single-line comments: --
            if self._current() == '-' and self._peek() == '-':
                self._skip_comment()
                continue

            # Numbers
            if self._current().isdigit():
                tokens.append(self._read_number())
                continue

            # String literals
            if self._current() in ("'", '"'):
                tokens.append(self._read_string())
                continue

            # Identifiers and keywords
            if self._current().isalpha() or self._current() == '_':
                tokens.append(self._read_identifier_or_keyword())
                continue

            # Two-character operators
            start_col = self.column
            if self._current() == '!' and self._peek() == '=':
                self._advance()
                self._advance()
                tokens.append(Token(TokenType.NOT_EQUALS, '!=', self.line, start_col))
                continue
            if self._current() == '<' and self._peek() == '=':
                self._advance()
                self._advance()
                tokens.append(Token(TokenType.LESS_EQUAL, '<=', self.line, start_col))
                continue
            if self._current() == '>' and self._peek() == '=':
                self._advance()
                self._advance()
                tokens.append(Token(TokenType.GREATER_EQUAL, '>=', self.line, start_col))
                continue

            # Single-character operators and punctuation
            if self._current() == '<':
                self._advance()
                tokens.append(Token(TokenType.LESS, '<', self.line, start_col))
                continue
            if self._current() == '>':
                self._advance()
                tokens.append(Token(TokenType.GREATER, '>', self.line, start_col))
                continue
            if self._current() == '=':
                self._advance()
                tokens.append(Token(TokenType.EQUALS, '=', self.line, start_col))
                continue

            if self._current() in SINGLE_CHAR_TOKENS:
                ch = self._advance()
                tokens.append(Token(SINGLE_CHAR_TOKENS[ch], ch, self.line, start_col))
                continue

            # Unknown character
            bad = self._current()
            raise LexerError(f"Unexpected character: {bad!r}", self.line, self.column)

        tokens.append(Token(TokenType.EOF, '', self.line, self.column))
        return tokens
