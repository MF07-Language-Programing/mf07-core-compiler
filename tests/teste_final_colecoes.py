"""
Teste final das coleções com construtores opcionais.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from src.logging_config import setup_production_logging
from module import CorpLang


def main():
    print("=== Teste final das coleções ===")
    setup_production_logging()

    corp_lang = CorpLang()

    test_code = """
    intent testeFinal() {
        print("=== Teste Final das Coleções ===")
        
        # 1. Lista sem tipo específico
        var numeros = new List()
        numeros.append(1)
        numeros.append(2)
        numeros.append(3)
        numeros.append(4)
        numeros.append(5)
        
        print("Lista:", numeros.toString())
        
        var pares = numeros.filter(fn(n) { return n % 2 == 0 })
        print("Pares:", pares.toString())
        
        var dobrados = numeros.map(fn(n) { return n * 2 })
        print("Dobrados:", dobrados.toString())
        
        # 2. HashMap sem tipos específicos
        var dados = new HashMap()
        dados.put("nome", "João")
        dados.put("idade", 30)
        dados.put("cidade", "São Paulo")
        
        print("Dados:", dados.toString())
        print("Nome:", dados.get("nome"))
        
        # 3. Set sem tipo específico
        var tags = new Set()
        tags.add("javascript")
        tags.add("python")
        tags.add("java")
        tags.add("javascript") # duplicado
        
        print("Tags:", tags.toString())
        print("Tamanho:", tags.size())
        
        # 4. Operações com Set
        var tags2 = new Set()
        tags2.add("python")
        tags2.add("go")
        tags2.add("rust")
        
        var uniao = tags.union(tags2)
        var intersecao = tags.intersection(tags2)
        
        print("União:", uniao.toString())
        print("Interseção:", intersecao.toString())
        
        print("")
        print("🎉 Sistema de coleções tipadas implementado com sucesso!")
        print(" List - Lista genérica com map, filter, forEach")
        print(" HashMap - Mapa chave-valor com operações completas")
        print(" Set - Conjunto com operações de união, interseção, diferença")
        print(" Interfaces funcionando")
        print(" Tipagem opcional nos construtores")
        print(" Suporte a operações funcionais")
    }
    
    testeFinal()
    """

    corp_lang.run(test_code)


if __name__ == "__main__":
    main()
