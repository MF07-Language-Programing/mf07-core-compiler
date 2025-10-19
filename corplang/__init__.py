"""
corplang package

This package provides a stable, minimal API surface that wraps the existing
monolithic `module.py` implementation. The goal is to centralize public
symbols here and provide a migration path to split the implementation into
smaller modules (lexer, parser, ast, interpreter) without changing external
imports used by tools and tests.

When you refactor functionality out of `module.py`, update the imports in
these small wrappers to re-export the same symbols.
"""
from ..src import lexer as _lexer
from ..src import parser as _parser
from ..src import lang_ast as _ast
from ..src import interpreter as _interpreter

# Re-export common API
CorpLang = _interpreter.CorpLang
Interpreter = _interpreter.Interpreter
Lexer = _lexer.Lexer
Parser = _parser.Parser

# AST nodes (convenience)
Program = _ast.Program
FunctionDeclaration = _ast.FunctionDeclaration
VarDeclaration = _ast.VarDeclaration
ReturnStatement = _ast.ReturnStatement
Literal = _ast.Literal
Identifier = _ast.Identifier

__all__ = [
    'CorpLang', 'Interpreter', 'Lexer', 'Parser',
    'Program', 'FunctionDeclaration', 'VarDeclaration', 'ReturnStatement',
    'Literal', 'Identifier'
]
