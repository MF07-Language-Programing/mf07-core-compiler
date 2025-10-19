from src.lexer import Lexer
from pathlib import Path
p = Path(__file__).resolve().parents[1] / 'examples' / 'sample_project' / 'main.mp'
s = p.read_text(encoding='utf-8')
lex = Lexer(s)
toks = lex.tokenize()
for i,t in enumerate(toks):
    print(i, t.line, t.column, t.type.name, repr(t.value))
