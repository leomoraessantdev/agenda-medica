"""Configuracao central de logging: console + arquivo rotativo em logs/app.log."""
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

from flask import Flask

_FORMATO = "%(asctime)s %(levelname)s [%(name)s] %(message)s"
_configurado = False


def configure_logging(app: Flask) -> None:
    """Configura o logging global uma unica vez (idempotente).

    Escreve em console e em logs/app.log com rotacao, para que qualquer falha
    tratada na Parte 2 fique registrada de forma persistente.
    """
    global _configurado
    if _configurado:
        return

    nivel_nome = app.config.get("LOG_LEVEL", "INFO").upper()
    nivel = getattr(logging, nivel_nome, logging.INFO)

    logs_dir = Path(app.root_path).parent / "logs"
    logs_dir.mkdir(exist_ok=True)

    formatter = logging.Formatter(_FORMATO)

    arquivo = RotatingFileHandler(
        logs_dir / "app.log", maxBytes=1_000_000, backupCount=5, encoding="utf-8"
    )
    arquivo.setFormatter(formatter)

    console = logging.StreamHandler()
    console.setFormatter(formatter)

    root = logging.getLogger()
    root.setLevel(nivel)
    root.handlers.clear()
    root.addHandler(arquivo)
    root.addHandler(console)

    _configurado = True
