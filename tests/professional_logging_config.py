"""
Configuração de logging profissional para CorpLang.
Logs otimizadas para produção com informações essenciais.
"""

from src.logger import LogLevel, configure_logger, set_component_level


def setup_professional_logging():
    """
    Configurar logging profissional com informações essenciais.
    Remove logs verbosas mantendo apenas o necessário para monitoramento.
    """
    # Configurar logger global com formato limpo
    configure_logger(
        level=LogLevel.INFO,
        show_timestamp=False,
        show_level=False,  # Remove [INFO], [DEBUG] para limpar saída
        show_component=False,  # Remove componente por padrão
        use_colors=True,
    )

    # Core loading - apenas resumo final, não cada arquivo
    set_component_level("core-loader", LogLevel.INFO)

    # Parser/Lexer - apenas erros críticos
    set_component_level("parser", LogLevel.ERROR)
    set_component_level("lexer", LogLevel.ERROR)

    # Interpreter - apenas erros e avisos importantes
    set_component_level("interpreter", LogLevel.WARN)

    # Type checker - manter para mostrar erros de tipo
    set_component_level("type-checker", LogLevel.INFO)

    # Import system - apenas problemas críticos
    set_component_level("imports", LogLevel.ERROR)


def setup_minimal_logging():
    """
    Configurar logging mínimo - apenas saída do programa.
    Remove todas as logs do sistema interno.
    """
    configure_logger(
        level=LogLevel.ERROR,
        show_timestamp=False,
        show_level=False,
        show_component=False,
        use_colors=False,
    )

    # Silenciar todos os componentes internos
    set_component_level("core-loader", LogLevel.OFF)
    set_component_level("parser", LogLevel.ERROR)
    set_component_level("lexer", LogLevel.ERROR)
    set_component_level("interpreter", LogLevel.ERROR)
    set_component_level("type-checker", LogLevel.ERROR)
    set_component_level("imports", LogLevel.ERROR)


def setup_startup_summary_logging():
    """
    Configurar logging com resumo de inicialização.
    Mostra apenas um resumo do carregamento do core.
    """
    configure_logger(
        level=LogLevel.INFO,
        show_timestamp=False,
        show_level=False,
        show_component=False,
        use_colors=True,
    )

    # Configuração customizada para mostrar apenas resumo
    set_component_level("core-loader", LogLevel.INFO)
    set_component_level("parser", LogLevel.ERROR)
    set_component_level("lexer", LogLevel.ERROR)
    set_component_level("interpreter", LogLevel.WARN)
    set_component_level("type-checker", LogLevel.INFO)
    set_component_level("imports", LogLevel.ERROR)


def setup_development_concise_logging():
    """
    Configurar logging para desenvolvimento com informações úteis mas concisas.
    """
    configure_logger(
        level=LogLevel.INFO,
        show_timestamp=False,
        show_level=True,
        show_component=True,
        use_colors=True,
    )

    # Mostrar apenas informações relevantes para debug
    set_component_level("core-loader", LogLevel.INFO)
    set_component_level("parser", LogLevel.WARN)
    set_component_level("lexer", LogLevel.WARN)
    set_component_level("interpreter", LogLevel.INFO)
    set_component_level("type-checker", LogLevel.INFO)
    set_component_level("imports", LogLevel.INFO)


# Alias para facilitar uso
setup_prod = setup_professional_logging
setup_dev = setup_development_concise_logging
setup_quiet = setup_minimal_logging
setup_summary = setup_startup_summary_logging
