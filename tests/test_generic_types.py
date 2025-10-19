"""
Teste para verificar se tipagem genérica funciona no parser.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from src.logging_config import setup_production_logging
from module import CorpLang


def main():
    print("=== Teste de tipagem genérica ===")
    setup_production_logging()

    corp_lang = CorpLang()

    test_code = """
    intent testGenericTypes() {
        print("=== Testando tipagem genérica ===")
        
        # Teste com declaração de variável tipada
        var numbers: List<int> = new List()
        var names: List<string> = new List()
        
        numbers.append(1)
        numbers.append(2)
        numbers.append(3)
        
        names.append("João")
        names.append("Maria")
        names.append("Pedro")
        
        print("Números:", numbers.toString())
        print("Nomes:", names.toString())
        
        print("Teste de tipagem genérica concluído!")
    }
    
    testGenericTypes()
    """

    corp_lang.run(test_code)


if __name__ == "__main__":
    main()
