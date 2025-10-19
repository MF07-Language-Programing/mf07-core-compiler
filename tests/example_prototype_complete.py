"""
Exemplo completo demonstrando métodos prototype.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from src.logging_config import setup_production_logging
from module import CorpLang


def main():
    print("=== Exemplo completo de métodos prototype ===")
    setup_production_logging()

    corp_lang = CorpLang()

    test_code = """
    class Product {
        var name: string
        var price: float
        
        intent constructor(name: string, price: float) {
            this.name = name
            this.price = price
        }
        
        intent formatForDisplay(): string {
            var formattedName = this.name.upper()
            var formattedPrice = this.price.formatCurrency("BRL")
            return formattedName + " - " + formattedPrice
        }
        
        intent getNameLength(): int {
            return this.name.length
        }
        
        intent hasKeyword(keyword: string): bool {
            return this.name.lower().contains(keyword.lower())
        }
    }
    
    intent demonstratePrototypeMethods() {
        print("=== Demonstração de Métodos Prototype ===")
        
        # Criando produtos
        var laptop = new Product("Notebook Gamer", 2499.99)
        var mouse = new Product("Mouse Ergonômico", 89.50)
        
        print("Produtos criados:")
        print("1.", laptop.formatForDisplay())
        print("2.", mouse.formatForDisplay())
        
        # String methods
        print("\\nString methods:")
        var productName = "smartphone"
        print("Original:", productName)
        print("Upper:", productName.upper())
        print("Length:", productName.length)
        print("Contains 'smart':", productName.contains("smart"))
        print("Starts with 'smart':", productName.startsWith("smart"))
        print("Replaced:", productName.replace("smart", "mega"))
        
        # Number methods  
        print("\\nNumber methods:")
        var originalPrice: float = 1999.99
        var discount: int = 200
        var finalPrice = originalPrice - discount
        
        print("Original price:", originalPrice.formatCurrency("BRL"))
        print("Discount:", discount.formatCurrency("BRL"))
        print("Final price:", finalPrice.formatCurrency("BRL"))
        print("Final price (USD):", finalPrice.formatCurrency("USD"))
        print("Final price (2 decimals):", finalPrice.toFixed(2))
        print("Rounded:", finalPrice.round(0))
        
        # Usando em contexto
        print("\\nUsando em contexto real:")
        if (laptop.hasKeyword("gamer")) {
            print("Laptop é para gamers!")
            var nameLength = laptop.getNameLength()
            print("Nome tem", nameLength, "caracteres")
        }
        
        var searchTerm = "  mouse  "
        var cleanSearchTerm = searchTerm.trim().lower()
        if (mouse.hasKeyword(cleanSearchTerm)) {
            print("Mouse encontrado! Preço:", mouse.price.formatCurrency("BRL"))
        }
    }
    
    demonstratePrototypeMethods()
    """

    corp_lang.run(test_code)


if __name__ == "__main__":
    main()
