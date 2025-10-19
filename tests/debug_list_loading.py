"""
Debug para verificar se a classe List está sendo carregada como ClassObject.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from src.logging_config import setup_development_logging
from src.interpreter import Interpreter, ClassObject


def main():
    print("=== Debug do carregamento da classe List ===")
    setup_development_logging()

    interpreter = Interpreter()

    print("Valor inicial de List:", type(interpreter.globals.variables.get("List")))
    print("List inicial:", interpreter.globals.variables.get("List"))

    # Carregar core modules
    interpreter.load_core_modules()

    print("\nDepois do carregamento:")
    print("Valor final de List:", type(interpreter.globals.variables.get("List")))
    print("List final:", interpreter.globals.variables.get("List"))
    print(
        "É ClassObject?",
        isinstance(interpreter.globals.variables.get("List"), ClassObject),
    )

    if isinstance(interpreter.globals.variables.get("List"), ClassObject):
        list_class = interpreter.globals.variables.get("List")
        print(
            "Métodos da classe:",
            (
                list_class.methods.keys()
                if hasattr(list_class, "methods")
                else "No methods"
            ),
        )
        print(
            "Métodos estáticos:",
            (
                list_class.static_methods.keys()
                if hasattr(list_class, "static_methods")
                else "No static_methods"
            ),
        )


if __name__ == "__main__":
    main()
