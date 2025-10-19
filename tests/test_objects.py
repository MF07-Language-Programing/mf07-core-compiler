# Test core/objects.mp loading

import sys
from pathlib import Path

sys.path.append(".")

from src.lexer import Lexer
from src.parser import Parser
from src.interpreter import Interpreter


def test_objects_mp():
    core_path = Path("core/objects.mp")
    print(f"Testing {core_path}")

    with open(core_path, "r", encoding="utf-8") as f:
        src = f.read()

    print("Source code:")
    print(src)
    print("\n" + "=" * 50)

    try:
        print("Lexing...")
        lexer = Lexer(src)
        tokens = lexer.tokenize()
        print(f"Tokens generated: {len(tokens)}")

        print("Parsing...")
        parser = Parser(tokens)
        ast = parser.parse()
        print("AST generated successfully!")

        print("Interpreting...")
        interp = Interpreter()
        interp.interpret(ast)
        print("Interpretation successful!")

    except Exception as e:
        print(f"Error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    test_objects_mp()
