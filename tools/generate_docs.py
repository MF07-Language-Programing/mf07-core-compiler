"""Generate Markdown documentation from a running Interpreter's docs registry.

This script loads core modules using the project's Interpreter, then writes
`docs/generated_from_source.md` containing module-level, function and class docs.

Usage: python tools/generate_docs.py
"""

from src.interpreter import Interpreter
from src.lexer import Lexer
from src.parser import Parser
import os

OUT = os.path.join("docs", "generated_from_source.md")


def main():
    interp = Interpreter()
    # load core modules to populate docs
    interp.load_core_modules()

    entries = interp.docs
    if not entries:
        print("No docs found in interpreter registry.")
        return

    lines = ["# Generated documentation from source", ""]
    for name, meta in sorted(entries.items()):
        lines.append(f"## {name}")
        doc = meta.get("doc")
        if doc:
            lines.append(doc)
            lines.append("")
        params = meta.get("params")
        if params:
            lines.append("**Parameters:**")
            for p in params:
                ptypes = (
                    (meta.get("param_types") or {}).get(p)
                    if meta.get("param_types")
                    else None
                )
                lines.append(f"- {p}: {ptypes or 'any'}")
            lines.append("")
        ret = meta.get("return_type")
        if ret:
            lines.append(f"**Returns:** {ret}")
            lines.append("")
        if meta.get("type") == "class":
            methods = meta.get("methods") or {}
            if methods:
                lines.append("**Methods:**")
                for mname, mdoc in methods.items():
                    lines.append(f"- {mname}: {mdoc or ''}")
                lines.append("")

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(f"Wrote docs to {OUT}")


if __name__ == "__main__":
    main()
