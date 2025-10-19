"""
Exemplo simplificado focando nas funcionalidades básicas das coleções tipadas.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from src.logging_config import setup_production_logging
from module import CorpLang


def main():
    print("=== Exemplo das Coleções Tipadas ===")
    setup_production_logging()

    corp_lang = CorpLang()

    test_code = """
    # Definir interface básica
    interface Item {
        intent getName(): string
        intent getValue(): int
    }
    
    # Implementar classe que segue a interface
    class Product implements Item {
        private var name: string
        private var value: int
        
        intent constructor(name: string, value: int) {
            this.name = name
            this.value = value
        }
        
        intent getName(): string {
            return this.name
        }
        
        intent getValue(): int {
            return this.value
        }
        
        intent toString(): string {
            return this.name + " (R$ " + "{this.value}" + ")"
        }
    }
    
    intent exemploColecoesTipadas() {
        print("=== Demonstração das Coleções Tipadas ===")
        
        # 1. Lista tipada
        print("--- Lista tipada ---")
        var produtos = new List("Item")
        produtos.append(new Product("Notebook", 2500))
        produtos.append(new Product("Mouse", 150))
        produtos.append(new Product("Teclado", 200))
        
        print("Produtos na lista:")
        produtos.forEach(fn(produto) {
            print("- " + produto.toString())
        })
        
        # 2. HashMap tipado 
        print("")
        print("--- HashMap tipado ---")
        var estoque = new HashMap("string", "int")
        estoque.put("notebook", 5)
        estoque.put("mouse", 15) 
        estoque.put("teclado", 8)
        
        print("Estoque disponível:")
        estoque.forEach(fn(id, qtd) {
            print("- " + id + ": " + "{qtd}" + " unidades")
        })
        print("Estoque completo:", estoque.toString())
        
        # 3. Set tipado
        print("")
        print("--- Set tipado ---")
        var categorias = new Set("string")
        categorias.add("Eletrônicos")
        categorias.add("Informática")
        categorias.add("Periféricos")
        categorias.add("Eletrônicos") # Duplicado - será ignorado
        
        print("Categorias únicas:", categorias.toString())
        print("Total de categorias:", categorias.size())
        print("Tem 'Informática'?", categorias.has("Informática"))
        
        # 4. Operações avançadas com Set
        print("")
        print("--- Operações com Set ---")
        var tags1 = new Set("string")
        tags1.add("novo")
        tags1.add("promoção")
        tags1.add("destaque")
        
        var tags2 = new Set("string")
        tags2.add("promoção")
        tags2.add("desconto")
        tags2.add("oferta")
        
        var union = tags1.union(tags2)
        var intersection = tags1.intersection(tags2)
        var difference = tags1.difference(tags2)
        
        print("Tags1:", tags1.toString())
        print("Tags2:", tags2.toString())
        print("União:", union.toString())
        print("Interseção:", intersection.toString()) 
        print("Diferença:", difference.toString())
        
        # 5. Filtragem e transformação
        print("")
        print("--- Filtragem e transformação ---")
        var numeros = new List("int")
        numeros.append(1)
        numeros.append(2)
        numeros.append(3)
        numeros.append(4)
        numeros.append(5)
        
        var pares = numeros.filter(fn(n) { return n % 2 == 0 })
        var dobrados = numeros.map(fn(n) { return n * 2 })
        
        print("Números:", numeros.toString())
        print("Pares:", pares.toString())
        print("Dobrados:", dobrados.toString())
        
        print("")
        print("🎉 Exemplo completo executado com sucesso!")
        print("✓ List<T> - Lista tipada")
        print("✓ HashMap<K,V> - Mapa chave-valor tipado")
        print("✓ Set<T> - Conjunto tipado com operações")
        print("✓ Interfaces funcionando")
        print("✓ Métodos funcionais (map, filter, forEach)")
        print("✓ Operações de conjuntos (union, intersection, difference)")
    }
    
    exemploColecoesTipadas()
    """

    corp_lang.run(test_code)


if __name__ == "__main__":
    main()
