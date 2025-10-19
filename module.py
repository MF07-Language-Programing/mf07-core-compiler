"""Facade module for CorpLang runtime.

This file keeps the historical public API but delegates implementation to
the modularized code in the `src` package. It re-exports the main classes
and provides convenience functions used by CLI/tests.
"""

import os
from typing import Any

from tests.professional_logging_config import setup_professional_logging
from src.lexer import Lexer
from src.parser import Parser
from src.interpreter import Interpreter

# Initialize professional logging system
# Initialize logging system
setup_professional_logging()


class CorpLang:
    def __init__(self, strict_types: bool = True):
        self.interpreter = Interpreter()
        self.strict_types = strict_types

    def run(self, source_code: str):
        try:
            # Ensure core modules (core/*.mp) are loaded into the runtime
            try:
                self.interpreter.load_core_modules()
            except Exception as e:
                print(f"Aviso: falha ao carregar módulos core: {e}")
                # Continue — runtime remains usable even if core failed to load

            # optional static type check integration
            try:
                from src.runtime.type_checker import check_source as _check_source
            except Exception as ex:
                print(
                    "Aviso: type_checker não disponível, ignorando checagem de tipos."
                )
                print(ex)
                _check_source = lambda src: []

            try:
                print("Running type checker...")
                errors = _check_source(source_code)
            except Exception as e:
                print(f"Type checker error: {e}")
                errors = []

            if errors:
                for err in errors:
                    print(f"TypeError: {err}")
                if self.strict_types:
                    raise RuntimeError("Type checking failed")
                else:
                    print("Continuing despite type checker errors.")

            lexer = Lexer(source_code)
            tokens = lexer.tokenize()
            parser = Parser(tokens)
            ast = parser.parse()

            self.interpreter.interpret(ast)
        except Exception as e:
            print(f"Erro: {e}")
            raise

    def run_file(self, filename: str):
        try:
            with open(filename, "r", encoding="utf-8") as f:
                src = f.read()
            prev_dir = getattr(self.interpreter, "current_file_dir", os.getcwd())
            prev_path = getattr(self.interpreter, "current_file_path", None)
            self.interpreter.current_file_dir = os.path.dirname(
                os.path.abspath(filename)
            )
            self.interpreter.current_file_path = os.path.abspath(filename)
            try:
                self.run(src)
            finally:
                self.interpreter.current_file_dir = prev_dir
                self.interpreter.current_file_path = prev_path
        except FileNotFoundError:
            print(f"Arquivo '{filename}' não encontrado")
        except Exception as e:
            print(f"Erro ao executar arquivo: {e}")


def main():
    print("=== CorpLang - Linguagem de Programação Corporativa ===")
    lang = CorpLang()
    lang.run_file("test_await.mp")


if __name__ == "__main__":
    main()

# Backwards compatibility
MFLanguageExecutor = CorpLang
