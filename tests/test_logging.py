"""
Teste para verificar diferentes níveis de logging.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from src.logging_config import setup_production_logging
from module import CorpLang


def main():
    print("=== Teste com logging de produção (apenas WARN/ERROR) ===")
    setup_production_logging()

    # Executar exemplo
    corp_lang = CorpLang()

    # Código simples para testar
    test_code = """
    intent test() {
        print("Hello from MF07 with production logging!")
        var x: int = 42
        print("Value:", x)
    }
    
    test()
    """

    corp_lang.run(test_code)


if __name__ == "__main__":
    main()
