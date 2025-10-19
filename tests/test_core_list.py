"""
Teste para verificar se a classe List do core está funcionando.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from src.logging_config import setup_production_logging
from module import CorpLang


def main():
    print("=== Teste da classe List do core ===")
    setup_production_logging()

    corp_lang = CorpLang()

    test_code = """
    intent testCoreList() {
        print("=== Testando classe List do core ===")
        
        # Usar a classe List do core (não a NativeList)
        var numbers = new List()
        numbers.append(1)
        numbers.append(2)
        numbers.append(3)
        numbers.append(4)
        numbers.append(5)
        
        print("Lista original:", numbers.toString())
        print("Tamanho:", numbers.length())
        
        # Testar map
        var doubled = numbers.map(fn(x) { return x * 2 })
        print("Números dobrados:", doubled.toString())
        
        # Testar filter
        var evens = numbers.filter(fn(x) { return x % 2 == 0 })
        print("Números pares:", evens.toString())
        
        # Testar forEach
        print("Iterando com forEach:")
        numbers.forEach(fn(x) { print("- Número:", x) })
        
        # Testar insert
        numbers.insert(2, 99)
        print("Após inserir 99 na posição 2:", numbers.toString())
        
        # Testar removeAt
        var removed = numbers.removeAt(2)
        print("Removido:", removed)
        print("Lista após remoção:", numbers.toString())
    }
    
    testCoreList()
    """

    corp_lang.run(test_code)


if __name__ == "__main__":
    main()
