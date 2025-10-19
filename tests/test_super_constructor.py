import io
import sys
import os

from src.interpreter import Interpreter


def run_code_and_capture(src, cwd=None):
    interp = Interpreter()
    if cwd:
        interp.current_file_dir = cwd
    old_stdout = sys.stdout
    buf = io.StringIO()
    sys.stdout = buf
    try:
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


def test_super_constructor_chain():
    src = """
class Base {
    var x: int = 0
    intent constructor(x: int) { this.x = x }
    intent getX() { return this.x }
}

class Derived extends Base {
    var y: int = 0
    intent constructor(x: int, y: int) {
        super(x)
        this.y = y
    }
    intent getY() { return this.y }
}

var d = new Derived(7, 13)
print("DX:", d.getX(), "DY:", d.getY())
"""
    out = run_code_and_capture(src)
    assert "DX:" in out
    assert "DY:" in out
    assert "7" in out
    assert "13" in out
