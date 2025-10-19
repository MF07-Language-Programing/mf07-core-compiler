"""Minimal pygls-based language server for CorpLang.

Provides:
- Completion for builtins and intent names parsed from the document (simple regex).
- Diagnostics by running `type_checker.check_source` on document change and returning diagnostics.

This server expects to be launched as: `python client/server.py` from the extension's root or via the Node launcher.
"""

from pygls.server import LanguageServer

# Avoid importing pygls.types directly to keep compatibility across pygls versions.
# We'll construct plain dicts matching the LSP wire format for completions and diagnostics.
from pathlib import Path
import re
import sys
import json

# Add repo root to path so we can import local type_checker
repo_root = Path(__file__).resolve().parents[2]
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

from runtime.type_checker import check_source

ls = LanguageServer("corp-lang", "1.0.0")

BUILTINS = [
    ("print", "Prints values"),
    ("parseJson", "Parses a JSON string"),
    ("stringifyJson", "Stringify an object to JSON"),
    ("getKeys", "Get keys of an object"),
    ("getValues", "Get values of an object"),
    ("waitSeconds", "Sleep for given seconds"),
]

FUNC_RE = re.compile(r"intent\s+(\w+)\s*\(")


@ls.feature("textDocument/completion")
def completions(ls, params):
    # Parse document for intent names and provide builtin + local intent completions
    items = []
    # Builtins
    for name, doc in BUILTINS:
        items.append({"label": name, "kind": 3, "detail": doc})

    # Attempt to include intent names from the current document
    try:
        doc = ls.workspace.get_document(params.textDocument.uri).source
        for m in FUNC_RE.finditer(doc):
            fname = m.group(1)
            items.append({"label": fname, "kind": 3, "detail": "user intent"})
    except Exception:
        pass

    return {"isIncomplete": False, "items": items}


@ls.feature("textDocument/hover")
def hover(ls, params):
    # Provide basic hover info for builtin functions
    try:
        uri = params.textDocument.uri
        doc = ls.workspace.get_document(uri).source
        pos = params.position
        # Extract the word at position (simple)
        lines = doc.splitlines()
        if pos.line < len(lines):
            line = lines[pos.line]
            # find word containing character
            import re as _re

            for w in _re.finditer(r"\b[a-zA-Z_]\w*\b", line):
                if w.start() <= pos.character <= w.end():
                    word = w.group(0)
                    for name, docstr in BUILTINS:
                        if name == word:
                            return {
                                "contents": {
                                    "kind": "markdown",
                                    "value": f"**{name}**\n\n{docstr}",
                                }
                            }
    except Exception:
        pass
    return None


def run_type_check(text):
    try:
        errs = check_source(text)
        diagnostics = []
        for e in errs:
            # Emit a general diagnostic at line 0 when no range info is available
            diagnostics.append(
                {
                    "range": {
                        "start": {"line": 0, "character": 0},
                        "end": {"line": 0, "character": 1},
                    },
                    "message": str(e),
                    "severity": 1,  # Error
                }
            )
        return diagnostics
    except Exception as ex:
        return [
            {
                "range": {
                    "start": {"line": 0, "character": 0},
                    "end": {"line": 0, "character": 1},
                },
                "message": str(ex),
                "severity": 1,
            }
        ]


@ls.feature("textDocument/didOpen")
def did_open(ls, params):
    text = params.textDocument.text
    diagnostics = run_type_check(text)
    ls.publish_diagnostics(params.textDocument.uri, diagnostics)


@ls.feature("textDocument/didChange")
def did_change(ls, params):
    # params.contentChanges is a list; take first full text
    text = params.contentChanges[0].text if params.contentChanges else ""
    diagnostics = run_type_check(text)
    ls.publish_diagnostics(params.textDocument.uri, diagnostics)


if __name__ == "__main__":
    ls.start_io()
