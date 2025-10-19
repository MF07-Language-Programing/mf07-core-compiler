"""
Teste para verificar se null e None estão funcionando.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from src.logging_config import setup_production_logging
from module import CorpLang


def main():
    print("=== Teste de null e None ===")
    setup_production_logging()

    corp_lang = CorpLang()

    test_code = """
    intent testNull() {
        print("=== Testando null e None ===")
        
        var x = null
        var y = None
        
        print("x =", x)
        print("y =", y)
        print("x == null:", x == null)
        print("y == None:", y == None)
        print("x == y:", x == y)
        
        if (x == null) {
            print("x é null - OK!")
        }
        
        if (y == None) {
            print("y é None - OK!")
        }
        
        # Teste com função que pode retornar null
        intent getValue(shouldReturnNull: bool) {
            if (shouldReturnNull) {
                return null
            }
            return "valor"
        }
        
        var result1 = getValue(true)
        var result2 = getValue(false)
        
        print("result1 (deve ser null):", result1)
        print("result2 (deve ser 'valor'):", result2)
        
        if (result1 == null) {
            print("result1 é null - correto!")
        }
        
        if (result2 != null) {
            print("result2 não é null - correto!")
        }
    }
    
    testNull()
    """

    corp_lang.run(test_code)


if __name__ == "__main__":
    main()
