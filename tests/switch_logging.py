"""
Script para alternar rapidamente entre diferentes níveis de logging.
Permite configurar o nível de logging do CorpLang facilmente.
"""

import sys
import os

# Adicionar o diretório raiz ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from tests.professional_logging_config import (
    setup_professional_logging,
    setup_minimal_logging,
    setup_startup_summary_logging,
    setup_development_concise_logging,
)


def show_help():
    """Mostra ajuda sobre os níveis de logging disponíveis."""
    print(
        """
🔧 CorpLang Logging Configurator

NÍVEIS DISPONÍVEIS:

  prod        📊 Profissional (Recomendado)
              - Apenas resumo do core + type checker
              - Saída limpa para produção
              
  dev         🛠️ Desenvolvimento Conciso  
              - Logs úteis com componentes
              - Balance entre debug e limpeza
              
  quiet       🤫 Silencioso
              - Apenas erros críticos
              - Saída totalmente limpa
              
  summary     📋 Resumo de Startup
              - Resumo de inicialização
              - Balanceado para desenvolvimento

EXEMPLOS:
  python switch_logging.py prod     # Configurar para produção
  python switch_logging.py dev      # Configurar para desenvolvimento
  python switch_logging.py quiet    # Configurar silencioso
  
ATUAL: Profissional (prod) - logs otimizadas 
"""
    )


def apply_logging_level(level):
    """Aplica o nível de logging especificado ao module.py"""

    module_file = "module.py"

    # Mapear níveis para funções
    level_map = {
        "prod": "setup_professional_logging",
        "professional": "setup_professional_logging",
        "dev": "setup_development_concise_logging",
        "development": "setup_development_concise_logging",
        "quiet": "setup_minimal_logging",
        "minimal": "setup_minimal_logging",
        "summary": "setup_startup_summary_logging",
        "startup": "setup_startup_summary_logging",
    }

    if level not in level_map:
        print(f"❌ Nível '{level}' não reconhecido!")
        show_help()
        return False

    function_name = level_map[level]

    # Ler arquivo atual
    try:
        with open(module_file, "r", encoding="utf-8") as f:
            content = f.read()
    except FileNotFoundError:
        print(f"❌ Arquivo {module_file} não encontrado!")
        return False

    # Substituir a linha de import e chamada da função
    lines = content.split("\n")

    for i, line in enumerate(lines):
        if line.strip().startswith("from professional_logging_config import"):
            lines[i] = f"from professional_logging_config import {function_name}"
        elif line.strip().endswith("_logging()"):
            lines[i] = f"# Initialize logging system\n{function_name}()"

    # Salvar arquivo modificado
    try:
        with open(module_file, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))

        level_names = {
            "prod": "Profissional",
            "dev": "Desenvolvimento Conciso",
            "quiet": "Silencioso",
            "summary": "Resumo de Startup",
        }

        print(f" Logging configurado para: {level_names.get(level, level)}")
        print(f"📝 Arquivo {module_file} atualizado")
        return True

    except Exception as e:
        print(f"❌ Erro ao salvar {module_file}: {e}")
        return False


if __name__ == "__main__":
    if len(sys.argv) != 2:
        show_help()
    else:
        level = sys.argv[1].lower()
        apply_logging_level(level)
