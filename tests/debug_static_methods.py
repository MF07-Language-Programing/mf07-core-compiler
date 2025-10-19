"""
Debug para verificar se a classe List tem static_methods.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from src.logging_config import setup_development_logging
from src.interpreter import Interpreter, ClassObject
from src.lexer import Lexer
from src.parser import Parser


def main():
    print("=== Debug static_methods da classe List ===")
    setup_development_logging()

    interpreter = Interpreter()

    # Carregar apenas o list.mp manualmente
    list_mp_path = os.path.join(os.getcwd(), "core", "list.mp")

    with open(list_mp_path, "r", encoding="utf-8") as f:
        src = f.read()

    lexer = Lexer(src)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    ast = parser.parse()

    interpreter.interpret(ast)

    # Verificar a classe List
    list_class = interpreter.globals.variables.get("List")
    print(f"Classe List: {type(list_class)}")
    print(f"É ClassObject? {isinstance(list_class, ClassObject)}")

    if isinstance(list_class, ClassObject):
        print(f"Tem static_methods? {hasattr(list_class, 'static_methods')}")
        if hasattr(list_class, "static_methods"):
            print(f"static_methods: {list_class.static_methods}")
            print(f"Quantidade de static_methods: {len(list_class.static_methods)}")

        print(f"Tem methods? {hasattr(list_class, 'methods')}")
        if hasattr(list_class, "methods"):
            print(f"methods: {list(list_class.methods.keys())}")


if __name__ == "__main__":
    main()
