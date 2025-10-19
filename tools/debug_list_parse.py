#!/usr/bin/env python3
"""Debug script to identify parser hang in core/list.mp"""

from src.lexer import Lexer
from src.parser import Parser
from pathlib import Path
import traceback


def debug_parse():
    list_file = Path(__file__).resolve().parents[1] / "core" / "list.mp"
    src = list_file.read_text(encoding="utf-8")

    print(f"=== Debugging core/list.mp ===")
    print(f"File size: {len(src)} chars")

    # Step 1: Tokenize
    print("\n--- Step 1: Tokenizing ---")
    lexer = Lexer(src)
    tokens = lexer.tokenize()
    print(f"Generated {len(tokens)} tokens")

    # Show first 50 and last 20 tokens
    print("\nFirst 50 tokens:")
    for i, tok in enumerate(tokens[:50]):
        print(
            f"  {i:03d}: {tok.type.name:15} {repr(tok.value):20} (L{tok.line:02d}C{tok.column:02d})"
        )

    print(f"\nLast 20 tokens:")
    start_idx = max(0, len(tokens) - 20)
    for i, tok in enumerate(tokens[start_idx:], start=start_idx):
        print(
            f"  {i:03d}: {tok.type.name:15} {repr(tok.value):20} (L{tok.line:02d}C{tok.column:02d})"
        )

    # Step 2: Parse with detailed tracing
    print("\n--- Step 2: Parsing with tracing ---")
    parser = Parser(tokens)

    # Monkey patch parser methods to add debug prints
    original_advance = parser.advance
    original_expect = parser.expect
    original_parse_statement = parser.parse_statement
    original_parse_class_declaration = parser.parse_class_declaration

    def traced_advance():
        old_pos = parser.pos
        old_token = parser.current_token
        original_advance()
        print(
            f"    ADVANCE: pos {old_pos} -> {parser.pos}, token {old_token.type.name if old_token else 'None'} -> {parser.current_token.type.name if parser.current_token else 'None'}"
        )

    def traced_expect(token_type):
        print(
            f"    EXPECT: {token_type.name}, current: {parser.current_token.type.name if parser.current_token else 'None'}"
        )
        return original_expect(token_type)

    def traced_parse_statement():
        print(
            f"  PARSE_STATEMENT: pos={parser.pos}, token={parser.current_token.type.name if parser.current_token else 'None'}"
        )
        try:
            result = original_parse_statement()
            print(
                f"  PARSE_STATEMENT result: {type(result).__name__ if result else 'None'}"
            )
            return result
        except Exception as e:
            print(f"  PARSE_STATEMENT error: {e}")
            raise

    def traced_parse_class_declaration():
        print(
            f"PARSE_CLASS_DECLARATION: starting at pos={parser.pos}, token={parser.current_token.type.name if parser.current_token else 'None'}"
        )
        result = original_parse_class_declaration()
        print(
            f"PARSE_CLASS_DECLARATION: finished, result={type(result).__name__ if result else 'None'}"
        )
        return result

    # Apply tracing
    parser.advance = traced_advance
    parser.expect = traced_expect
    parser.parse_statement = traced_parse_statement
    parser.parse_class_declaration = traced_parse_class_declaration

    try:
        ast = parser.parse()
        print(f"\n✓ Parse successful! AST has {len(ast.statements)} statements")
        for i, stmt in enumerate(ast.statements):
            print(f"  Statement {i}: {type(stmt).__name__}")
    except Exception as e:
        print(f"\n✗ Parse failed: {e}")
        print(f"Parser stopped at pos={parser.pos}/{len(parser.tokens)}")
        if parser.current_token:
            print(
                f"Current token: {parser.current_token.type.name} {repr(parser.current_token.value)} at L{parser.current_token.line}C{parser.current_token.column}"
            )
        traceback.print_exc()


if __name__ == "__main__":
    debug_parse()
