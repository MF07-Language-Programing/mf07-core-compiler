"""
Teste simples para debugar prototype methods.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from src.logging_config import setup_development_logging
from module import CorpLang


def main():
    print("=== Debug prototype methods ===")
    setup_development_logging()  # Usar desenvolvimento para ver todos os logs

    corp_lang = CorpLang()

    test_code = """
    intent debugTest() {
        var name = "test"
        print("name type:", type(name))
        print("name value:", name)
        print("name.upper():", name.upper())
    }
    
    debugTest()
    """

    corp_lang.run(test_code)


if __name__ == "__main__":
    main()
