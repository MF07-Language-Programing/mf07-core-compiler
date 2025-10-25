from src.lexer import Lexer

s = '"module doc"\n\nfunction myfn() {\n    "fn doc"\n    return 1\n}\n'
lex = Lexer(s)
toks = lex.tokenize()
for t in toks:
    print(t.type.name, repr(t.value), t.line, t.column)
