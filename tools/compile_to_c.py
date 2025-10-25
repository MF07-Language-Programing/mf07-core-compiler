"""Minimal transpiler from a small subset of CorpLang (.mp) AST to C.

This is an experimental AOT step: it supports a very small subset so you
can produce a native executable without Python for trivial scripts that
use top-level function declarations and calls and the built-in
`print`/`sout` functions with string/integer literals.

Limitations (current):
- Functions with no parameters (params ignored).
- Statements supported in function bodies: FunctionCall (print/sout) and Return (with literal).
- Expressions supported: Literal, Identifier (for simple calls), PropertyAccess not supported.
- No classes, no dynamic features, no imports.

Use as:
  python tools/compile_to_c.py examples/first_project/simple_example.mp -o generated.c
  gcc -o myprog generated.c

This gives a concrete starting point to expand toward a full native compiler
by gradually lowering runtime requirements and adding codegen for more AST nodes.
"""

import argparse
import sys
from typing import List
from pathlib import Path

# Make sure the project's `src/` folder is available on sys.path so this
# script can be executed directly (e.g. `python tools/compile_to_c.py ...`) from
# the repository root or from other working directories without requiring the
# user to set PYTHONPATH or install the package.
ROOT = Path(__file__).resolve().parent.parent
# Add project root so imports like `from src.lexer import ...` work
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.lexer import Lexer
from src.parser import Parser
from src.lang_ast import (
    Program,
    FunctionDeclaration,
    FunctionCall,
    Literal,
    Identifier,
    VarDeclaration,
    ReturnStatement,
)


def escape_c_string(s: str) -> str:
    return s.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")


class CEmitter:
    def __init__(self):
        self.funcs: List[FunctionDeclaration] = []
        self.top_calls: List[FunctionCall] = []

    def emit_program(self, program: Program) -> str:
        # Collect functions and top-level calls
        for stmt in program.statements:
            if isinstance(stmt, FunctionDeclaration):
                self.funcs.append(stmt)
            elif isinstance(stmt, FunctionCall):
                self.top_calls.append(stmt)
            elif isinstance(stmt, VarDeclaration):
                # skip simple top-level vars for now
                pass
            else:
                # ignore others for now
                pass

        parts = [
            "#include <stdio.h>",
            "#include <stdlib.h>",
            "#include <string.h>",
            "",
        ]

        # Forward declarations
        for f in self.funcs:
            parts.append(f"void {f.name}();")
        parts.append("")

        # Function definitions
        for f in self.funcs:
            parts.append(self.emit_function(f))

        # main
        parts.append("int main(int argc, char** argv) {")
        parts.append("    // top-level calls")
        for c in self.top_calls:
            parts.append("    " + self.emit_call_statement(c) + ";")
        parts.append("    return 0;")
        parts.append("}")

        return "\n".join(parts)

    def emit_function(self, f: FunctionDeclaration) -> str:
        body_lines: List[str] = []
        for stmt in f.body:
            if isinstance(stmt, FunctionCall):
                body_lines.append("    " + self.emit_call_statement(stmt) + ";")
            elif isinstance(stmt, ReturnStatement):
                if isinstance(stmt.value, Literal):
                    val = stmt.value.value
                    if isinstance(val, str):
                        body_lines.append(
                            f"    return; /* returning string literal ignored in C stub */"
                        )
                    else:
                        body_lines.append("    return;")
                else:
                    body_lines.append("    return;")
            else:
                body_lines.append("    /* unsupported stmt in function body */")

        body = "\n".join(body_lines) if body_lines else "    // empty body"
        return f"void {f.name}() {{\n{body}\n}}\n"

    def emit_call_statement(self, call: FunctionCall) -> str:
        # Only support Identifier callee
        callee = call.callee
        if isinstance(callee, Identifier):
            name = callee.name
            # builtins
            if name in ("print", "sout"):
                # only first arg handled and only literals
                if call.args:
                    a = call.args[0]
                    if isinstance(a, Literal):
                        v = a.value
                        if isinstance(v, str):
                            s = escape_c_string(v)
                            return f'printf("%s\\n", "{s}")'
                        else:
                            return f'printf("%d\\n", {int(v)})'
                return 'printf("\\n")'
            else:
                # assume a user function with no args
                return f"{name}()"
        else:
            return "/* unsupported callee */"


def main():
    p = argparse.ArgumentParser()
    p.add_argument("input", help="input .mp file")
    p.add_argument("-o", "--output", default="generated.c")
    args = p.parse_args()

    src = open(args.input, "r", encoding="utf-8").read()
    lex = Lexer(src)
    tokens = lex.tokenize()
    parser = Parser(tokens)
    program = parser.parse()

    emitter = CEmitter()
    out = emitter.emit_program(program)
    with open(args.output, "w", encoding="utf-8") as f:
        f.write(out)
    print(f"Wrote C to {args.output}")


if __name__ == "__main__":
    main()
