"""
Teste básico para verificar se interfaces funcionam.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from src.logging_config import setup_production_logging
from module import CorpLang


def main():
    print("=== Teste de interfaces ===")
    setup_production_logging()

    corp_lang = CorpLang()

    test_code = """
    # Definir uma interface
    interface Item {
        intent getName(): string
        intent getValue(): int
    }
    
    # Definir uma classe que implementa a interface
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
    }
    
    intent testInterface() {
        print("=== Testando interfaces ===")
        
        var product = new Product("Notebook", 2500)
        print("Produto:", product.getName())
        print("Valor:", product.getValue())
        
        print("Teste de interface concluído!")
    }
    
    testInterface()
    """

    corp_lang.run(test_code)


if __name__ == "__main__":
    main()
