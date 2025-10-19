"""
Script para configurar níveis de logging do MF07.

Usage:
  python configure_logs.py --level INFO --component core-loader=DEBUG
  python configure_logs.py --production
  python configure_logs.py --development
  python configure_logs.py --quiet
"""

import argparse
import sys
import os

# Add src to path so we can import logger modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from src.logger import LogLevel
from src.logging_config import (
    setup_default_logging,
    setup_development_logging,
    setup_production_logging,
    setup_quiet_logging,
)


def main():
    parser = argparse.ArgumentParser(description="Configure MF07 logging levels")

    # Preset configurations
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--development", action="store_true", help="Enable verbose development logging"
    )
    group.add_argument(
        "--production",
        action="store_true",
        help="Enable production logging (warnings/errors only)",
    )
    group.add_argument(
        "--quiet", action="store_true", help="Enable quiet logging (fatal errors only)"
    )
    group.add_argument(
        "--default", action="store_true", help="Enable default logging configuration"
    )

    # Custom configuration
    parser.add_argument(
        "--level",
        choices=["TRACE", "DEBUG", "INFO", "WARN", "ERROR", "FATAL", "OFF"],
        help="Set global logging level",
    )
    parser.add_argument(
        "--component",
        action="append",
        metavar="COMPONENT=LEVEL",
        help="Set specific component level (e.g., core-loader=DEBUG)",
    )

    # Output options
    parser.add_argument(
        "--no-colors", action="store_true", help="Disable colored output"
    )
    parser.add_argument(
        "--no-timestamp", action="store_true", help="Disable timestamp in logs"
    )
    parser.add_argument(
        "--no-component", action="store_true", help="Disable component names in logs"
    )

    args = parser.parse_args()

    if args.development:
        print("Configurando logging para desenvolvimento...")
        setup_development_logging()
    elif args.production:
        print("Configurando logging para produção...")
        setup_production_logging()
    elif args.quiet:
        print("Configurando logging silencioso...")
        setup_quiet_logging()
    elif args.default or not any([args.level, args.component]):
        print("Configurando logging padrão...")
        setup_default_logging()
    else:
        # Custom configuration
        from src.logger import configure_logger, set_component_level, set_log_level

        # Apply global level if specified
        if args.level:
            level = getattr(LogLevel, args.level)
            set_log_level(level)
            print(f"Nível global definido para: {args.level}")

        # Apply component levels if specified
        if args.component:
            for comp_level in args.component:
                if "=" not in comp_level:
                    print(f"Formato inválido: {comp_level}. Use COMPONENT=LEVEL")
                    continue
                comp, level_str = comp_level.split("=", 1)
                try:
                    level = getattr(LogLevel, level_str.upper())
                    set_component_level(comp, level)
                    print(f"Componente '{comp}' definido para: {level_str.upper()}")
                except AttributeError:
                    print(f"Nível inválido: {level_str}")

        # Apply formatting options
        if args.no_colors or args.no_timestamp or args.no_component:
            configure_logger(
                show_timestamp=not args.no_timestamp,
                show_component=not args.no_component,
                use_colors=not args.no_colors,
            )
            print("Formatação personalizada aplicada.")

    print("Configuração de logging aplicada com sucesso!")
    print("\nNíveis disponíveis: TRACE, DEBUG, INFO, WARN, ERROR, FATAL, OFF")
    print(
        "Componentes principais: core-loader, parser, lexer, interpreter, type-checker, imports"
    )


if __name__ == "__main__":
    main()
