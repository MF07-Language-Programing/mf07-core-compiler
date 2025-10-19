"""
Teste para verificar se a classe List do core está funcionando com logs completos.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from src.logging_config import setup_development_logging
from module import CorpLang


def main():
    print("=== Teste da classe List do core com logs verbosos ===")
    setup_development_logging()

    corp_lang = CorpLang()

    test_code = """
    intent testCoreList() {
        print("=== Testando classe List do core ===")
        
        # Primeiro vamos ver se existe List global
        print("Verificando se List existe...")
        
        # Usar a classe List do core (não a NativeList)
        var numbers = new List()
        numbers.append(1)
        numbers.append(2)
        numbers.append(3)
        
        print("Lista criada:", numbers.toString())
        print("Tamanho:", numbers.length())
    }
    
    testCoreList()
    """

    corp_lang.run(test_code)


if __name__ == "__main__":
    main()
