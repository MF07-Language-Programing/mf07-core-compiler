# CorpLang VS Code Extension

This folder contains a lightweight VS Code extension skeleton providing:

- TextMate grammar for syntax highlighting for files with extension `.mp`.
- Optional snippets for common constructs (async intent, intent).

Installation
1. From the root of this folder, install vsce: `npm install -g vsce`
2. Package the extension: `vsce package` which will produce a .vsix file.
3. Install the .vsix in VS Code via the Extensions view ("Install from VSIX...").

Or, instead of packaging, simply add the following to your workspace settings to associate .mp files with this language:

```json
"files.associations": {
  "*.mp": "corplang"
}
```

Next steps
- Add a simple Language Server (LSP) in `client/` to provide IntelliSense, hover and diagnostics.
- Expand the TextMate grammar to better capture intent names, imports and template strings.

Running the built-in Python LSP (optional)

The `client/server.py` file is a minimal Python language server using `pygls` that provides basic completions and diagnostics (it runs `type_checker.py`). To use it you need `pygls` installed in the workspace venv:

```powershell
env\Scripts\python.exe -m pip install pygls
```

Then install the extension (VSIX) and open a `.mp` file — the extension will attempt to launch the server via the workspace venv Python.

Quick package & install (Windows)
1. Install vsce if you haven't: `npm install -g vsce`
2. From project root run the helper script:

```powershell
.\corp-lang-vscode\package_and_install.ps1
```

What to expect once installed
- Open any `.mp` file (for example `examples/sample_project/main.mp`).
- Syntax highlighting will apply (colors for keywords, types, strings and comments).
- If you want autocompletion/diagnostics, start the LSP server task in VS Code:
  - Run Task -> Start CorpLang LSP
  - Then completions for builtins and intent names will be available; diagnostics come from the project's `type_checker.py`.

