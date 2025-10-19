"""
Teste das novas classes de coleções HashMap, Set e List tipadas.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from src.logging_config import setup_production_logging
from module import CorpLang


def main():
    print("=== Teste de coleções tipadas ===")
    setup_production_logging()

    corp_lang = CorpLang()

    test_code = """
    intent testTypedCollections() {
        print("=== Testando coleções tipadas ===")
        
        # Teste HashMap
        print("--- HashMap ---")
        var map = new HashMap("string", "int")
        map.put("idade", 25)
        map.put("altura", 180)
        map.put("peso", 75)
        
        print("Idade:", map.get("idade"))
        print("Tamanho do map:", map.size())
        print("Map completo:", map.toString())
        
        # Teste Set
        print("--- Set ---")
        var numeros = new Set("int")
        numeros.add(1)
        numeros.add(2)
        numeros.add(3)
        numeros.add(2) # Duplicado - deve ser ignorado
        
        print("Tem 2?", numeros.has(2))
        print("Tamanho do set:", numeros.size())
        print("Set completo:", numeros.toString())
        
        # Teste List tipada
        print("--- List tipada ---")
        var nomes = new List("string")
        nomes.append("João")
        nomes.append("Maria")
        nomes.append("Pedro")
        
        print("Nomes:", nomes.toString())
        print("Tamanho da lista:", nomes.length())
        
        print("Teste de coleções tipadas concluído!")
    }
    
    testTypedCollections()
    """

    corp_lang.run(test_code)


if __name__ == "__main__":
    main()
