"""Configuracao por ambiente, lida de variaveis de ambiente."""
import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

# Raiz do projeto (pasta que contem o pacote app/). Usada para montar um
# caminho absoluto do banco, valido tanto em Docker quanto no terminal local.
BASE_DIR = Path(__file__).resolve().parent.parent
_DEFAULT_DB = f"sqlite:///{(BASE_DIR / 'instance' / 'agenda.sqlite3').as_posix()}"


class BaseConfig:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-inseguro")
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", _DEFAULT_DB)
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"

    AGENDAMENTOS_API_URL = os.getenv(
        "AGENDAMENTOS_API_URL", "http://localhost:5001/agendamentos"
    )
    AGENDAMENTOS_API_TIMEOUT = int(os.getenv("AGENDAMENTOS_API_TIMEOUT", "5"))


class DevelopmentConfig(BaseConfig):
    DEBUG = True


class ProductionConfig(BaseConfig):
    DEBUG = False


class TestingConfig(BaseConfig):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"


CONFIG_BY_NAME: dict[str, type[BaseConfig]] = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
}


def get_config(name: str | None = None) -> type[BaseConfig]:
    name = name or os.getenv("FLASK_ENV", "development")
    return CONFIG_BY_NAME.get(name, DevelopmentConfig)
