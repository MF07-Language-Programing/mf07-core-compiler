import re
import json
from typing import Any, List, Optional
from enum import Enum
from dataclasses import dataclass


# ========== TOKENS E LEXER ==========
class TokenType(Enum):

    # Estruturas JSON
    NULL = "NULL"
    ARRAY = "ARRAY"
    OBJECT = "OBJECT"

    # Literais
    NUMBER = "NUMBER"
    STRING = "STRING"
    BOOLEAN = "BOOLEAN"

    # Identificadores
    IDENTIFIER = "IDENTIFIER"

    # Operadores
    PLUS = "PLUS"
    MINUS = "MINUS"
    MULTIPLY = "MULTIPLY"
    DIVIDE = "DIVIDE"
    MODULO = "MODULO"

    # Comparação
    EQUAL = "EQUAL"
    NOT_EQUAL = "NOT_EQUAL"
    LESS_THAN = "LESS_THAN"
    GREATER_THAN = "GREATER_THAN"
    LESS_EQUAL = "LESS_EQUAL"
    GREATER_EQUAL = "GREATER_EQUAL"

    # Lógicos
    AND = "AND"
    OR = "OR"
    NOT = "NOT"

    # Atribuição
    ASSIGN = "ASSIGN"

    # Palavras-chave
    VAR = "VAR"
    FUNCTION = "FUNCTION"
    FN = "FN"  # lambda intent
    IF = "IF"
    ELSE = "ELSE"
    WHILE = "WHILE"
    FOR = "FOR"
    IN = "IN"
    OF = "OF"
    RETURN = "RETURN"
    TRY = "TRY"
    CATCH = "CATCH"
    FINALLY = "FINALLY"
    THROW = "THROW"
    # Classes / OOP
    CLASS = "CLASS"
    EXTENDS = "EXTENDS"
    IMPLEMENTS = "IMPLEMENTS"
    INTERFACE = "INTERFACE"
    ABSTRACT = "ABSTRACT"
    SUPER = "SUPER"
    STATIC = "STATIC"
    PRIVATE = "PRIVATE"
    PUBLIC = "PUBLIC"
    NEW = "NEW"
    THIS = "THIS"

    # Específico para dados corporativos
    DATASET = "DATASET"
    MODEL = "MODEL"
    PREDICT = "PREDICT"
    TRAIN = "TRAIN"
    ANALYZE = "ANALYZE"
    IMPORT = "IMPORT"
    ASYNC = "ASYNC"
    AWAIT = "AWAIT"

    # Delimitadores
    LPAREN = "LPAREN"
    RPAREN = "RPAREN"
    LBRACE = "LBRACE"
    RBRACE = "RBRACE"
    LBRACKET = "LBRACKET"
    RBRACKET = "RBRACKET"
    SEMICOLON = "SEMICOLON"
    COLON = "COLON"
    COMMA = "COMMA"
    DOT = "DOT"

    # Especiais
    NEWLINE = "NEWLINE"
    EOF = "EOF"
    WHITESPACE = "WHITESPACE"


@dataclass
class Token:
    type: TokenType
    value: str
    line: int
    column: int


class Lexer:
    def __init__(self, text: str):
        self.text = text
        self.pos = 0
        self.line = 1
        self.column = 1
        self.tokens: List[Token] = []

        # Palavras-chave
        self.keywords = {
            "var": TokenType.VAR,
            "intent": TokenType.FUNCTION,
            "fn": TokenType.FN,
            "async": TokenType.ASYNC,
            "await": TokenType.AWAIT,
            "class": TokenType.CLASS,
            "extends": TokenType.EXTENDS,
            "implements": TokenType.IMPLEMENTS,
            "interface": TokenType.INTERFACE,
            "abstract": TokenType.ABSTRACT,
            "static": TokenType.STATIC,
            "private": TokenType.PRIVATE,
            "public": TokenType.PUBLIC,
            "new": TokenType.NEW,
            "this": TokenType.THIS,
            "super": TokenType.SUPER,
            "if": TokenType.IF,
            "else": TokenType.ELSE,
            "while": TokenType.WHILE,
            "for": TokenType.FOR,
            "in": TokenType.IN,
            "of": TokenType.OF,
            "return": TokenType.RETURN,
            "true": TokenType.BOOLEAN,
            "false": TokenType.BOOLEAN,
            "null": TokenType.NULL,
            "None": TokenType.NULL,
            "and": TokenType.AND,
            "or": TokenType.OR,
            "not": TokenType.NOT,
            "dataset": TokenType.DATASET,
            "model": TokenType.MODEL,
            "predict": TokenType.PREDICT,
            "train": TokenType.TRAIN,
            "analyze": TokenType.ANALYZE,
            "import": TokenType.IMPORT,
            "try": TokenType.TRY,
            "catch": TokenType.CATCH,
            "finally": TokenType.FINALLY,
            "throw": TokenType.THROW,
        }

    def current_char(self) -> Optional[str]:
        if self.pos >= len(self.text):
            return None
        return self.text[self.pos]

    def peek_char(self) -> Optional[str]:
        peek_pos = self.pos + 1
        if peek_pos >= len(self.text):
            return None
        return self.text[peek_pos]

    def advance(self):
        if self.pos < len(self.text) and self.text[self.pos] == "\n":
            self.line += 1
            self.column = 1
        else:
            self.column += 1
        self.pos += 1

    def skip_whitespace(self):
        while True:
            c = self.current_char()
            if c is None or c not in " \t\r":
                break
            self.advance()

    def read_json_like_structure(self) -> str:
        """Reads JSON-like structures such as objects or arrays without breaking tokenization."""
        start_char = self.current_char()

        # Define expected closing character
        matching = {"{": "}", "[": "]"}
        if start_char not in matching:
            raise ValueError(f"Invalid start character: '{start_char}'")

        end_char = matching[start_char]
        bracket_count = 0
        result = ""

        while self.current_char():
            char = self.current_char()
            if char is None:
                break
            result += char

            if char == start_char:
                bracket_count += 1
            elif char == end_char:
                bracket_count -= 1

            self.advance()

            if bracket_count == 0:
                break

        if bracket_count != 0:
            raise SyntaxError(f"Unbalanced structure: expected matching '{end_char}'")

        return result

    def read_number(self) -> str:
        num_str = ""
        while True:
            c = self.current_char()
            if c is None:
                break
            if c.isdigit() or c == ".":
                num_str += c
                self.advance()
            else:
                break
        return num_str

    def read_string(self) -> str:
        quote_char = self.current_char()
        if quote_char is None:
            return ""
        assert quote_char in ("'", '"')
        self.advance()  # Skip opening quote

        string_val = ""
        while self.current_char() is not None and self.current_char() != quote_char:
            if self.current_char() == "\\":
                self.advance()
                c = self.current_char()
                if c is None:
                    break
                if c == "n":
                    string_val += "\n"
                elif c == "t":
                    string_val += "\t"
                elif c == "r":
                    string_val += "\r"
                elif c == "\\":
                    string_val += "\\"
                elif c == quote_char:
                    string_val += quote_char
                else:
                    string_val += c
            else:
                c = self.current_char()
                if c is None:
                    break
                string_val += c
            self.advance()

        if self.current_char() == quote_char:
            self.advance()  # Skip closing quote

        return string_val

    def read_identifier(self) -> str:
        identifier = ""
        while True:
            c = self.current_char()
            if c is None:
                break
            if not (c.isalnum() or c == "_"):
                break
            identifier += c
            self.advance()
        return identifier

    def last_significant_char(self):
        i = self.pos - 1
        while i >= 0 and self.text[i] in " \t\r\n":
            i -= 1
        if i >= 0:
            return self.text[i]
        return ""

    def tokenize(self) -> List[Token]:
        while self.current_char():
            c = self.current_char()
            if c is None:
                break

            if c in " \t\r":
                self.skip_whitespace()
                continue

            if c == "\n":
                self.tokens.append(
                    Token(TokenType.NEWLINE, "\n", self.line, self.column)
                )
                self.advance()
                continue

            if self.current_char() == "#":
                # Skip comments
                while self.current_char() and self.current_char() != "\n":
                    self.advance()
                continue

            # Detectar Objetos BSON ou Arrays JSON-like
            if self.current_char() == "{":
                prev_char = self.last_significant_char()
                if prev_char in (":", "=", "(", "[", ","):
                    json_str = self.read_json_like_structure()
                    try:
                        json.loads(json_str)
                        self.tokens.append(
                            Token(TokenType.OBJECT, json_str, self.line, self.column)
                        )
                        continue
                    except json.JSONDecodeError as e:
                        print(e)
                        print("Não é um JSON válido.")
                        # Não trata manualmente — o loop principal continuará e vai lidar com '{'
                        self.pos -= len(json_str) - 1
                        self.column -= len(json_str) - 1

            elif self.current_char() == "[":
                prev_char = self.last_significant_char()
                if prev_char in (":", "=", "(", "[", ","):
                    json_str = self.read_json_like_structure()
                    try:
                        json.loads(json_str)
                        self.tokens.append(
                            Token(TokenType.ARRAY, json_str, self.line, self.column)
                        )
                        continue
                    except json.JSONDecodeError:
                        print("Não é um array JSON válido.")
                        self.pos -= len(json_str) - 1
                        self.column -= len(json_str) - 1

            c = self.current_char()
            if c is not None and c.isdigit():
                num = self.read_number()
                self.tokens.append(Token(TokenType.NUMBER, num, self.line, self.column))
                continue

            c = self.current_char()
            if c is not None and c in "\"'":
                string_val = self.read_string()
                self.tokens.append(
                    Token(TokenType.STRING, string_val, self.line, self.column)
                )
                continue

            c = self.current_char()
            if c is not None and (c.isalpha() or c == "_"):
                identifier = self.read_identifier()
                token_type = self.keywords.get(identifier, TokenType.IDENTIFIER)
                self.tokens.append(
                    Token(token_type, identifier, self.line, self.column)
                )
                continue

            # Operadores e delimitadores
            char = self.current_char()
            line, col = self.line, self.column

            if char == "+":
                self.tokens.append(Token(TokenType.PLUS, "+", line, col))
            elif char == "-":
                self.tokens.append(Token(TokenType.MINUS, "-", line, col))
            elif char == "*":
                self.tokens.append(Token(TokenType.MULTIPLY, "*", line, col))
            elif char == "/":
                self.tokens.append(Token(TokenType.DIVIDE, "/", line, col))
            elif char == "%":
                self.tokens.append(Token(TokenType.MODULO, "%", line, col))
            elif char == "=":
                self.advance()
                if self.current_char() == "=":
                    self.tokens.append(Token(TokenType.EQUAL, "==", line, col))
                else:
                    self.pos -= 1
                    self.column -= 1
                    self.tokens.append(Token(TokenType.ASSIGN, "=", line, col))
            elif char == "!":
                self.advance()
                if self.current_char() == "=":
                    self.tokens.append(Token(TokenType.NOT_EQUAL, "!=", line, col))
                else:
                    self.pos -= 1
                    self.column -= 1
                    self.tokens.append(Token(TokenType.NOT, "!", line, col))
            elif char == "<":
                self.advance()
                if self.current_char() == "=":
                    self.tokens.append(Token(TokenType.LESS_EQUAL, "<=", line, col))
                else:
                    self.pos -= 1
                    self.column -= 1
                    self.tokens.append(Token(TokenType.LESS_THAN, "<", line, col))
            elif char == ">":
                self.advance()
                if self.current_char() == "=":
                    self.tokens.append(Token(TokenType.GREATER_EQUAL, ">=", line, col))
                else:
                    self.pos -= 1
                    self.column -= 1
                    self.tokens.append(Token(TokenType.GREATER_THAN, ">", line, col))
            elif char == "(":
                self.tokens.append(Token(TokenType.LPAREN, "(", line, col))
            elif char == ")":
                self.tokens.append(Token(TokenType.RPAREN, ")", line, col))
            elif char == "{":
                self.tokens.append(Token(TokenType.LBRACE, "{", line, col))
            elif char == "}":
                self.tokens.append(Token(TokenType.RBRACE, "}", line, col))
            elif char == "[":
                self.tokens.append(Token(TokenType.LBRACKET, "[", line, col))
            elif char == "]":
                self.tokens.append(Token(TokenType.RBRACKET, "]", line, col))
            elif char == ";":
                self.tokens.append(Token(TokenType.SEMICOLON, ";", line, col))
            elif char == ":":
                self.tokens.append(Token(TokenType.COLON, ":", line, col))
            elif char == ",":
                self.tokens.append(Token(TokenType.COMMA, ",", line, col))
            elif char == ".":
                self.tokens.append(Token(TokenType.DOT, ".", line, col))
            else:
                raise SyntaxError(
                    f"Caractere inesperado '{char}' na linha {line}, coluna {col}"
                )

            self.advance()

        self.tokens.append(Token(TokenType.EOF, "", self.line, self.column))
        return self.tokens


__all__ = ["TokenType", "Token", "Lexer"]
