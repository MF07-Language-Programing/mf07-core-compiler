"""
Teste para verificar se existem funções de conversão disponíveis.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from src.logging_config import setup_production_logging
from module import CorpLang


def main():
    print("=== Teste de funções de conversão ===")
    setup_production_logging()

    corp_lang = CorpLang()

    test_code = """
    intent testConversion() {
        print("Testando conversões...")
        
        var num = 42
        print("Número:", num)
        print("Type do número:", type(num))
        
        # Testar template strings
        var templateStr = "O número é: {num}"
        print("Template string:", templateStr)
        
        # Ver se str existe
        print("Type de str (se existir):", type(str))
    }
    
    testConversion()
    """

    corp_lang.run(test_code)


if __name__ == "__main__":
    main()
