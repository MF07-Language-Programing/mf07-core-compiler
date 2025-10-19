"""
Sistema de logging customizado para MF07 Language.

Fornece logging profissional com diferentes níveis, formatação customizável
e controle de verbosidade para uso interno do compilador/interpreter.
"""

import sys
import time
from enum import Enum
from typing import Any, Optional, Dict, Callable, TextIO
from datetime import datetime


class LogLevel(Enum):
    """Níveis de logging disponíveis."""

    TRACE = 0  # Detalhes extremos de execução
    DEBUG = 1  # Informações de debug detalhadas
    INFO = 2  # Informações gerais
    WARN = 3  # Avisos
    ERROR = 4  # Erros
    FATAL = 5  # Erros fatais
    OFF = 99  # Desabilitar logging


class LogFormatter:
    """Formatador de mensagens de log."""

    def __init__(
        self,
        show_timestamp: bool = True,
        show_level: bool = True,
        show_component: bool = True,
        timestamp_format: str = "%H:%M:%S.%f",
        use_colors: bool = True,
    ):
        self.show_timestamp = show_timestamp
        self.show_level = show_level
        self.show_component = show_component
        self.timestamp_format = timestamp_format
        self.use_colors = use_colors and sys.stderr.isatty()

        # Cores ANSI para diferentes níveis
        self.colors = {
            LogLevel.TRACE: "\033[90m",  # Cinza
            LogLevel.DEBUG: "\033[36m",  # Ciano
            LogLevel.INFO: "\033[32m",  # Verde
            LogLevel.WARN: "\033[33m",  # Amarelo
            LogLevel.ERROR: "\033[31m",  # Vermelho
            LogLevel.FATAL: "\033[35m",  # Magenta
        }
        self.reset = "\033[0m"

    def format(self, level: LogLevel, component: str, message: str) -> str:
        """Formatar mensagem de log."""
        parts = []

        # Timestamp
        if self.show_timestamp:
            now = datetime.now()
            timestamp = now.strftime(self.timestamp_format)[
                :-3
            ]  # Remove últimos 3 dígitos dos microsegundos
            parts.append(f"[{timestamp}]")

        # Level
        if self.show_level:
            level_str = level.name.ljust(5)
            if self.use_colors and level in self.colors:
                level_str = f"{self.colors[level]}{level_str}{self.reset}"
            parts.append(f"[{level_str}]")

        # Component
        if self.show_component and component:
            comp_str = component.ljust(2)
            parts.append(f"[{comp_str}]")

        # Message
        formatted = " ".join(parts)
        if formatted:
            formatted += " "
        formatted += message

        return formatted


class Logger:
    """Logger principal do MF07."""

    def __init__(
        self,
        name: str = "mf07",
        level: LogLevel = LogLevel.INFO,
        formatter: Optional[LogFormatter] = None,
        output: Optional[TextIO] = None,
    ):
        self.name = name
        self.level = level
        self.formatter = formatter or LogFormatter()
        self.output = output or sys.stderr
        self.components: Dict[str, LogLevel] = {}

    def set_level(self, level: LogLevel):
        """Definir nível de log global."""
        self.level = level

    def set_component_level(self, component: str, level: LogLevel):
        """Definir nível específico para um componente."""
        self.components[component] = level

    def get_effective_level(self, component: str) -> LogLevel:
        """Obter nível efetivo para um componente."""
        return self.components.get(component, self.level)

    def should_log(self, level: LogLevel, component: str = "") -> bool:
        """Verificar se deve fazer log para este nível/componente."""
        effective_level = self.get_effective_level(component)
        return level.value >= effective_level.value and effective_level != LogLevel.OFF

    def log(self, level: LogLevel, message: str, component: str = "", **kwargs):
        """Fazer log de uma mensagem."""
        if not self.should_log(level, component):
            return

        # Interpolar argumentos na mensagem se fornecidos
        if kwargs:
            try:
                message = message.format(**kwargs)
            except (KeyError, ValueError):
                pass  # Usar mensagem original se interpolação falhar

        formatted = self.formatter.format(level, component, message)
        print(formatted, file=self.output, flush=True)

    def trace(self, message: str, component: str = "", **kwargs):
        """Log nível TRACE."""
        self.log(LogLevel.TRACE, message, component, **kwargs)

    def debug(self, message: str, component: str = "", **kwargs):
        """Log nível DEBUG."""
        self.log(LogLevel.DEBUG, message, component, **kwargs)

    def info(self, message: str, component: str = "", **kwargs):
        """Log nível INFO."""
        self.log(LogLevel.INFO, message, component, **kwargs)

    def warn(self, message: str, component: str = "", **kwargs):
        """Log nível WARN."""
        self.log(LogLevel.WARN, message, component, **kwargs)

    def error(self, message: str, component: str = "", **kwargs):
        """Log nível ERROR."""
        self.log(LogLevel.ERROR, message, component, **kwargs)

    def fatal(self, message: str, component: str = "", **kwargs):
        """Log nível FATAL."""
        self.log(LogLevel.FATAL, message, component, **kwargs)


# Logger global da linguagem MF07
_default_logger: Optional[Logger] = None


def get_logger() -> Logger:
    """Obter logger global padrão."""
    global _default_logger
    if _default_logger is None:
        _default_logger = Logger()
    return _default_logger


def configure_logger(
    level: LogLevel = LogLevel.INFO,
    show_timestamp: bool = True,
    show_level: bool = True,
    show_component: bool = True,
    use_colors: bool = True,
) -> Logger:
    """Configurar logger global com parâmetros especificados."""
    global _default_logger
    formatter = LogFormatter(
        show_timestamp=show_timestamp,
        show_level=show_level,
        show_component=show_component,
        use_colors=use_colors,
    )
    _default_logger = Logger(level=level, formatter=formatter)
    return _default_logger


def set_log_level(level: LogLevel):
    """Definir nível de log global."""
    get_logger().set_level(level)


def set_component_level(component: str, level: LogLevel):
    """Definir nível específico para um componente."""
    get_logger().set_component_level(component, level)


# Funções de conveniência para logging
def trace(message: str, component: str = "", **kwargs):
    """Log TRACE usando logger global."""
    get_logger().trace(message, component, **kwargs)


def debug(message: str, component: str = "", **kwargs):
    """Log DEBUG usando logger global."""
    get_logger().debug(message, component, **kwargs)


def info(message: str, component: str = "", **kwargs):
    """Log INFO usando logger global."""
    get_logger().info(message, component, **kwargs)


def warn(message: str, component: str = "", **kwargs):
    """Log WARN usando logger global."""
    get_logger().warn(message, component, **kwargs)


def error(message: str, component: str = "", **kwargs):
    """Log ERROR usando logger global."""
    get_logger().error(message, component, **kwargs)


def fatal(message: str, component: str = "", **kwargs):
    """Log FATAL usando logger global."""
    get_logger().fatal(message, component, **kwargs)


# Contexto para logging temporário
class LogContext:
    """Context manager para ajustar logging temporariamente."""

    def __init__(
        self,
        level: Optional[LogLevel] = None,
        component_levels: Optional[Dict[str, LogLevel]] = None,
    ):
        self.level = level
        self.component_levels = component_levels or {}
        self.old_level: Optional[LogLevel] = None
        self.old_component_levels: Dict[str, LogLevel] = {}

    def __enter__(self):
        logger = get_logger()

        # Salvar níveis atuais
        if self.level is not None:
            self.old_level = logger.level
            logger.set_level(self.level)

        for comp, level in self.component_levels.items():
            self.old_component_levels[comp] = logger.get_effective_level(comp)
            logger.set_component_level(comp, level)

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        logger = get_logger()

        # Restaurar níveis anteriores
        if self.old_level is not None:
            logger.set_level(self.old_level)

        for comp, old_level in self.old_component_levels.items():
            logger.set_component_level(comp, old_level)
