from src.lexer import Lexer
from src.parser import Parser

s = '"module doc"\n\nfunction myfn() {\n    "fn doc"\n    return 1\n}\n'
lex = Lexer(s)
toks = lex.tokenize()
print("TOKENS:")
for i, t in enumerate(toks):
    print(i, t.type.name, repr(t.value), t.line, t.column)

p = Parser(toks)
try:
    ast = p.parse()
    print("Parsed successfully")
    print(ast)
except Exception as e:
    print("EXCEPTION:", e)
    print(
        "pos", p.pos, "current", p.current_token.type.name if p.current_token else None
    )
    import traceback

    traceback.print_exc()
