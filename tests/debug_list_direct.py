"""
Teste direto da classe List para ver se ela realmente existe.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from src.logging_config import setup_production_logging
from module import CorpLang


def main():
    print("=== Teste direto da classe List ===")
    setup_production_logging()

    corp_lang = CorpLang()

    # Primeiro, vamos verificar se List está no namespace
    test_code = """
    print("Tipo de List:", type(List))
    print("List é class?", List)
    
    # Tentar criar uma instância
    var lista = new List()
    print("Lista criada com sucesso!")
    lista.append("teste")
    lista.append("teste_2")
    print("Item adicionado!")
    print("Tamanho da lista:", lista.length())
    print("Conteúdo:", lista.toString())
    """

    corp_lang.run(test_code)


if __name__ == "__main__":
    main()
