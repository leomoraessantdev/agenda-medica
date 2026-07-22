"""ApiService: integracao HTTP com a API de agendamentos.

Concentra toda a comunicacao externa: timeout, tratamento de excecoes, logs,
validacao da resposta e fallback. Nunca deixa uma resposta invalida quebrar a
aplicacao -- em qualquer falha devolve uma lista vazia e um aviso amigavel.
"""
import logging
from dataclasses import dataclass, field

import requests
from flask import current_app

from app.exceptions.domain import (
    ApiIndisponivelError,
    ApiRespostaInvalidaError,
    CampoObrigatorioAusenteError,
)
from app.models.agendamento import Agendamento

logger = logging.getLogger(__name__)

_MSG_INDISPONIVEL = (
    "Nao foi possivel carregar os agendamentos agora. Tente novamente em instantes."
)
_MSG_INCOMPLETOS = "Alguns registros foram ignorados por dados incompletos."


@dataclass
class ResultadoAgendamentos:
    """Resultado seguro devolvido ao chamador (nunca lanca excecao)."""

    agendamentos: list[Agendamento] = field(default_factory=list)
    aviso: str | None = None


class ApiService:
    def __init__(self, base_url=None, timeout=None, session=None) -> None:
        self._base_url = base_url
        self._timeout = timeout
        self._session = session or requests

    def _config(self) -> tuple[str, int]:
        base = self._base_url or current_app.config["AGENDAMENTOS_API_URL"]
        timeout = self._timeout or current_app.config["AGENDAMENTOS_API_TIMEOUT"]
        return base, timeout

    def listar_agendamentos(self) -> ResultadoAgendamentos:
        """Ponto de entrada resiliente: sempre devolve ResultadoAgendamentos."""
        try:
            brutos = self._buscar()
            agendamentos, ignorados = self._validar(brutos)
        except ApiIndisponivelError as exc:
            logger.warning("API de agendamentos indisponivel (%s); fallback.", exc)
            return ResultadoAgendamentos(aviso=_MSG_INDISPONIVEL)
        except ApiRespostaInvalidaError as exc:
            logger.error("Resposta da API fora do contrato (%s); fallback.", exc)
            return ResultadoAgendamentos(aviso=_MSG_INDISPONIVEL)

        aviso = _MSG_INCOMPLETOS if ignorados else None
        return ResultadoAgendamentos(agendamentos=agendamentos, aviso=aviso)

    def _buscar(self) -> list:
        base, timeout = self._config()
        try:
            resposta = self._session.get(base, timeout=timeout)
        except requests.Timeout as exc:
            raise ApiIndisponivelError("timeout") from exc
        except requests.ConnectionError as exc:
            raise ApiIndisponivelError("erro de conexao") from exc
        except requests.RequestException as exc:
            raise ApiIndisponivelError("falha na requisicao") from exc

        if resposta.status_code >= 500:
            raise ApiIndisponivelError(f"status {resposta.status_code}")
        if resposta.status_code != 200:
            raise ApiRespostaInvalidaError(f"status {resposta.status_code}")

        try:
            dados = resposta.json()
        except ValueError as exc:
            raise ApiRespostaInvalidaError("corpo nao e JSON valido") from exc

        if not isinstance(dados, list):
            raise ApiRespostaInvalidaError("formato inesperado (esperava lista)")
        return dados

    def _validar(self, brutos: list) -> tuple[list[Agendamento], int]:
        validos: list[Agendamento] = []
        ignorados = 0
        for item in brutos:
            if not isinstance(item, dict):
                ignorados += 1
                logger.warning("Registro ignorado: nao e um objeto JSON.")
                continue
            try:
                validos.append(Agendamento.from_dict(item))
            except CampoObrigatorioAusenteError as exc:
                ignorados += 1
                logger.warning("Registro ignorado: %s", exc)
        return validos, ignorados
