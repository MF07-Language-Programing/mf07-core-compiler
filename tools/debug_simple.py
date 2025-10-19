#!/usr/bin/env python3
"""Debug script simples para identificar onde o parser trava em list.mp"""

from src.lexer import Lexer
from src.parser import Parser
from pathlib import Path
import signal
import sys


def timeout_handler(signum, frame):
    print("TIMEOUT! Parser travou - interrompendo...")
    sys.exit(1)


def debug_parse_simple():
    list_file = Path(__file__).resolve().parents[1] / "core" / "list.mp"
    src = list_file.read_text(encoding="utf-8")

    print(f"=== Debug core/list.mp ===")

    # Tokenize
    lexer = Lexer(src)
    tokens = lexer.tokenize()
    print(f"Tokens: {len(tokens)}")

    # Mostrar tokens ao redor de CLASS
    for i, tok in enumerate(tokens[:20]):
        print(f"  {i:03d}: {tok.type.name:15} {repr(tok.value):20}")

    # Parse com timeout
    parser = Parser(tokens)

    # Monkey patch para rastrear onde trava
    original_parse_class = parser.parse_class_declaration

    call_count = [0]

    def traced_parse_class():
        call_count[0] += 1
        if call_count[0] > 50:
            print(
                f"ERRO: parse_class_declaration chamada {call_count[0]} vezes! Loop infinito detectado."
            )
            print(f"Posição atual: {parser.pos}/{len(parser.tokens)}")
            if parser.current_token:
                print(
                    f"Token atual: {parser.current_token.type.name} {repr(parser.current_token.value)}"
                )
            sys.exit(1)

        print(
            f"parse_class_declaration #{call_count[0]} - pos={parser.pos}, token={parser.current_token.type.name if parser.current_token else 'None'}"
        )
        return original_parse_class()

    parser.parse_class_declaration = traced_parse_class

    try:
        ast = parser.parse()
        print(f"✓ Parse OK! {len(ast.statements)} statements")
    except Exception as e:
        print(f"✗ Parse falhou: {e}")


if __name__ == "__main__":
    debug_parse_simple()
