from src.lexer import Lexer
from src.parser import Parser
import os
import traceback

core_dir = os.path.join(os.getcwd(), "core")
if not os.path.isdir(core_dir):
    print("No core dir:", core_dir)
    raise SystemExit(1)

files = sorted([f for f in os.listdir(core_dir) if f.endswith(".mp")])
for fname in files:
    path = os.path.join(core_dir, fname)
    print("\n---", fname)
    src = open(path, "r", encoding="utf-8").read()
    print("LEN", len(src))
    try:
        lexer = Lexer(src)
        tokens = lexer.tokenize()
        print("TOKENS:", len(tokens))
        preview = [(t.type.name, t.value) for t in tokens[:80]]
        print("PREVIEW", preview)
    except Exception as e:
        print("LEX ERROR", e)
        traceback.print_exc()
        continue
    try:
        parser = Parser(tokens)
        ast = parser.parse()
        print("PARSE OK")
    except Exception as e:
        print("PARSE ERROR", e)
        traceback.print_exc()
        continue
print("\nDone")
