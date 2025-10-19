"""
Configuração de logging para MF07.

Configure os níveis de logging para diferentes componentes aqui.
"""

from .logger import LogLevel, configure_logger, set_component_level


def setup_default_logging():
    """Configurar logging padrão para MF07."""
    # Configurar logger global para INFO por padrão
    configure_logger(
        level=LogLevel.INFO,
        show_timestamp=False,  # Simplificar saída por padrão
        show_level=True,
        show_component=True,
        use_colors=True,
    )

    # Configurar níveis específicos por componente
    # Para desenvolvimento/debug, ajuste estes níveis:

    # Core module loading - usar DEBUG para ver detalhes
    set_component_level("core-loader", LogLevel.DEBUG)

    # Core module loading - usar DEBUG para ver detalhes
    set_component_level("mf.strict.https", LogLevel.DEBUG)

    # Parser - geralmente WARN ou ERROR, muito verboso no DEBUG
    set_component_level("parser", LogLevel.WARN)

    # Lexer - geralmente WARN ou ERROR, muito verboso no DEBUG
    set_component_level("lexer", LogLevel.WARN)

    # Interpreter - INFO para execução normal
    set_component_level("interpreter", LogLevel.INFO)

    # Type checker - INFO para mostrar erros de tipo
    set_component_level("type-checker", LogLevel.INFO)

    # Import system - DEBUG para troubleshooting imports
    set_component_level("imports", LogLevel.DEBUG)


def setup_development_logging():
    """Configurar logging para desenvolvimento com mais detalhes."""
    configure_logger(
        level=LogLevel.DEBUG,
        show_timestamp=True,
        show_level=True,
        show_component=True,
        use_colors=True,
    )

    # Todos componentes em DEBUG para desenvolvimento
    set_component_level("core-loader", LogLevel.TRACE)
    set_component_level("parser", LogLevel.DEBUG)
    set_component_level("lexer", LogLevel.DEBUG)
    set_component_level("interpreter", LogLevel.DEBUG)
    set_component_level("type-checker", LogLevel.DEBUG)
    set_component_level("imports", LogLevel.DEBUG)


def setup_production_logging():
    """Configurar logging para produção - apenas erros e avisos."""
    configure_logger(
        level=LogLevel.WARN,
        show_timestamp=False,
        show_level=False,
        show_component=False,
        use_colors=False,
    )

    # Em produção, mostrar apenas problemas
    set_component_level("core-loader", LogLevel.ERROR)
    set_component_level("parser", LogLevel.ERROR)
    set_component_level("lexer", LogLevel.ERROR)
    set_component_level("interpreter", LogLevel.ERROR)
    set_component_level("type-checker", LogLevel.WARN)
    set_component_level("imports", LogLevel.ERROR)


def setup_quiet_logging():
    """Configurar logging silencioso - apenas erros fatais."""
    configure_logger(level=LogLevel.FATAL, use_colors=False)
