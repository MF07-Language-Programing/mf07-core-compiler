from src.lexer import Lexer
from src.parser import Parser

# Test just the parser without type checker
code = """
intent test() {
    for (var i: int = 0; i < 5; i = i + 1) {
        print(i);
    }
}
"""

print("Testing parser only...")
lexer = Lexer(code)
tokens = lexer.tokenize()
parser = Parser(tokens)

try:
    ast = parser.parse()
    print(" Parser succeeded!")
    print(f"AST: {ast}")
except Exception as e:
    print(f"❌ Parser failed: {e}")
