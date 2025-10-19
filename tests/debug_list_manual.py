"""
Debug muito específico do carregamento do list.mp.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from src.logging_config import setup_development_logging
from src.interpreter import Interpreter, ClassObject
from src.lexer import Lexer
from src.parser import Parser


def main():
    print("=== Debug específico do list.mp ===")
    setup_development_logging()

    interpreter = Interpreter()

    # Verificar namespace antes
    print("Namespace inicial (List):", interpreter.globals.variables.get("List"))

    # Carregar apenas o list.mp manualmente
    list_mp_path = os.path.join(os.getcwd(), "core", "list.mp")
    print(f"Carregando {list_mp_path}")

    with open(list_mp_path, "r", encoding="utf-8") as f:
        src = f.read()

    # Snapshot antes
    before_keys = set(interpreter.globals.variables.keys())
    print(f"Chaves antes: {len(before_keys)} -> {sorted(before_keys)}")

    # Parse e interpret
    lexer = Lexer(src)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    ast = parser.parse()

    print("AST parseada, interpretando...")
    interpreter.interpret(ast)

    # Verificar depois
    after_keys = set(interpreter.globals.variables.keys())
    new_keys = after_keys - before_keys
    print(f"Novas chaves após interpretação: {sorted(new_keys)}")

    # Verificar especificamente List
    list_value = interpreter.globals.variables.get("List")
    print(f"Valor de List após interpretação: {type(list_value)} -> {list_value}")
    print(f"É ClassObject? {isinstance(list_value, ClassObject)}")

    # Verificar todas as chaves que contém "List"
    list_keys = [k for k in after_keys if "List" in k or "list" in k]
    print(f"Chaves relacionadas a List: {list_keys}")

    for key in list_keys:
        value = interpreter.globals.variables.get(key)
        print(f"  {key}: {type(value)} -> {value}")


if __name__ == "__main__":
    main()
