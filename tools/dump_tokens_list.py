from src.lexer import Lexer
from pathlib import Path

p = Path(__file__).resolve().parents[1] / "core" / "list.mp"
s = p.read_text(encoding="utf-8")
lex = Lexer(s)
toks = lex.tokenize()
print(f"Total tokens: {len(toks)}\n")
print("First 200 tokens:")
for i, t in enumerate(toks[:200]):
    print(f"{i:04d}: {t.type.name:20} {repr(t.value)} (line {t.line}, col {t.column})")
print("\nLast 20 tokens:")
start = max(0, len(toks) - 20)
for i, t in enumerate(toks[start:], start=start):
    print(f"{i:04d}: {t.type.name:20} {repr(t.value)} (line {t.line}, col {t.column})")
