"""
Debug direto da classe List para entender o problema.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from src.logging_config import setup_development_logging
from src.interpreter import Interpreter
from src.lexer import Lexer
from src.parser import Parser


def main():
    print("=== Debug da classe List ===")
    setup_development_logging()

    interpreter = Interpreter()

    # Testar só a definição da classe List
    test_code = """
    class TestList {
        intent constructor() {
            print("TestList criada!")
        }
        
        intent test() {
            return "funcionando"
        }
    }
    """

    try:
        lexer = Lexer(test_code)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()

        # Verificar namespace antes
        print("Namespace antes:", list(interpreter.globals.variables.keys()))

        interpreter.interpret(ast)

        # Verificar namespace depois
        print("Namespace depois:", list(interpreter.globals.variables.keys()))

        # Testar usar a classe
        test_use = """
        var obj = new TestList()
        print("Resultado:", obj.test())
        """

        lexer2 = Lexer(test_use)
        tokens2 = lexer2.tokenize()
        parser2 = Parser(tokens2)
        ast2 = parser2.parse()
        interpreter.interpret(ast2)

    except Exception as e:
        print(f"Erro: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
