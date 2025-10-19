# LSP Client placeholder

This folder is a placeholder for a Language Server implementation. Typical options:

- Node-based: implement a language server with `vscode-languageclient` + `vscode-languageserver`.
- Python-based: implement an LSP server using `pygls` and start it from the extension.

Minimum features to implement:
- CompletionProvider that returns builtins (print, parseJson, stringifyJson, etc.) and intent names parsed from the buffer.
- HoverProvider returning docstrings or short descriptions for builtins.
- Diagnostics: run the `type_checker.py` in a worker and return diagnostics.

If you want, I can scaffold a minimal Python-based language server using `pygls` that runs from the extension and provides completions for builtins and simple diagnostics using `type_checker.py`.
