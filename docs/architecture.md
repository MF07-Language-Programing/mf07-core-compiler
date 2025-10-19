# CorpLang Architecture (overview)

This document describes a recommended organization for the CorpLang implementation
so it's easy to extend with new AST nodes and processing logic.

Goals
- Break the monolithic `module.py` into smaller, testable units:
  - lexer.py: tokenization only
  - parser.py: parsing into AST nodes
  - ast.py: AST dataclasses for all node types
  - interpreter.py: runtime, builtins, execution
  - type_checker.py: static checking
- Provide a stable public API in `corplang/__init__.py` so external tools/tests
  don't need to change during refactors.
- Allow customizing language features via `language_config.yaml`.

Extension workflow
1. Add new AST node in `ast.py` (dataclass + docstring).
2. Add parsing rule to `parser.py` that builds the node.
3. Add evaluation/interpretation logic in `interpreter.py`.
4. Add unit tests for the lexer/parser/interpreter for the new feature.
5. Update `corplang/__init__.py` to re-export any new public symbols if needed.

Design notes
- AST nodes should include optional `line` and `column` fields to improve
  diagnostics.
- The interpreter should avoid global state; create an `Interpreter` instance
  per execution and pass configuration via constructor.
- Builtins should be registered via a registry so tests can replace them.
- Use the `language_config.yaml` file to make keywords, roots and builtin
  lists configurable without changing source code.

Testing
- Keep unit tests small and focused. Add parser tests that assert exact AST
  shapes. Add interpreter tests that run snippets and assert side-effects
  (return values, printed output, dataset/model simulator state).

Migration plan
- Keep `module.py` as the canonical implementation for now and use wrappers
  in `corplang/__init__.py` to maintain compatibility.
- When splitting, progressively move code into new modules and update
  the wrapper to re-export symbols from the new modules.


