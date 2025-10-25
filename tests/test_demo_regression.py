import io
import sys
import os

from src.interpreter import Interpreter


def run_demo_and_capture(path):
    interp = Interpreter()
    # Run the demo by importing as module path
    # Use current file's directory as current_file_dir
    interp.current_file_dir = os.path.dirname(os.path.abspath(path))
    interp.current_file_path = os.path.abspath(path)
    src = open(path, "r", encoding="utf-8").read()
    # Capture stdout
    old_stdout = sys.stdout
    buf = io.StringIO()
    sys.stdout = buf
    try:
        # Tokenize, parse and interpret
        from src.lexer import Lexer
        from src.parser import Parser

        lexer = Lexer(src)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()
        interp.interpret(ast)
    finally:
        sys.stdout = old_stdout
    return buf.getvalue()


def test_demo_outputs():
    demo = os.path.join("examples", "first_project", "models", "demo_class_system.mp")
    out = run_demo_and_capture(demo)
    print(out)
    # Basic assertions that key demo lines appear
    assert "Demonstrating class system features" in out
    assert "Creating animals" in out
    assert "--- Demonstrating polymorphism and lists ---" in out
    assert "Rex says: woof!" in out
    assert "Dog secret via method: top-secret" in out
