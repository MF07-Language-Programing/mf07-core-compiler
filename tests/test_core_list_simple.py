"""
Teste mais simples e específico para a classe List do core.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from src.logging_config import setup_production_logging
from module import CorpLang


def main():
    print("=== Teste simples da classe List do core ===")
    setup_production_logging()

    corp_lang = CorpLang()

    test_code = """
    intent testCoreListSimple() {
        print("=== Testando classe List do core ===")
        
        # Criar lista e adicionar alguns números
        var numbers = new List()
        numbers.append(1)
        numbers.append(2)
        numbers.append(3)
        
        print("Lista criada")
        print("Tamanho:", numbers.length())
        
        # Testar toString com números
        print("Conteúdo da lista:", numbers.toString())
        
        # Criar nova lista e testar map com números
        var doubled = numbers.map(fn(x) { return x * 2 })
        print("Números dobrados:", doubled.toString())
        
        print("Teste concluído com sucesso!")
    }
    
    testCoreListSimple()
    """

    corp_lang.run(test_code)


if __name__ == "__main__":
    main()
