"""
Teste para verificar métodos prototype em tipos primitivos.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from src.logging_config import setup_production_logging
from module import CorpLang


def main():
    print("=== Teste de métodos prototype ===")
    setup_production_logging()

    corp_lang = CorpLang()

    test_code = """
    intent testPrototypeMethods() {
        print("=== Testando métodos prototype ===")
        
        # String methods
        var name: string = "João Silva"
        print("name:", name)
        print("name.upper():", name.upper())
        print("name.lower():", name.lower())
        print("name.length:", name.length)
        print("name.contains('João'):", name.contains("João"))
        print("name.startsWith('João'):", name.startsWith("João"))
        print("name.endsWith('Silva'):", name.endsWith("Silva"))
        print("name.replace('João', 'Maria'):", name.replace("João", "Maria"))
        
        var text = "  hello world  "
        print("text.trim():", text.trim())
        
        # Number methods
        var price: int = 1234
        print("price:", price)
        print("price.toString():", price.toString())
        print("price.formatCurrency('BRL'):", price.formatCurrency("BRL"))
        print("price.formatCurrency('USD'):", price.formatCurrency("USD"))
        print("price.toFixed(2):", price.toFixed(2))
        
        var amount: float = 1234.567
        print("amount:", amount)
        print("amount.formatCurrency('BRL'):", amount.formatCurrency("BRL"))
        print("amount.toFixed(2):", amount.toFixed(2))
        print("amount.round(2):", amount.round(2))
        print("amount.abs():", amount.abs())
        
        var negative = -42
        print("negative.abs():", negative.abs())
    }
    
    testPrototypeMethods()
    """

    corp_lang.run(test_code)


if __name__ == "__main__":
    main()
