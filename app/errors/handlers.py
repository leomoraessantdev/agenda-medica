"""Handlers globais de erro: nunca vazam stack trace ao usuario; logam e respondem amigavel."""
import logging

from flask import Flask, jsonify, render_template, request
from werkzeug.exceptions import HTTPException

from app import messages
from app.exceptions.domain import BancoIndisponivelError, DomainError

logger = logging.getLogger(__name__)


def register_error_handlers(app: Flask) -> None:
    @app.errorhandler(BancoIndisponivelError)
    def _banco_indisponivel(erro):
        logger.error("Banco de dados indisponivel: %s", erro)
        return _responder(503, messages.BANCO_INDISPONIVEL)

    @app.errorhandler(DomainError)
    def _dominio(erro):
        logger.error("Erro de dominio nao tratado: %s", erro)
        return _responder(500, messages.ERRO_INESPERADO)

    @app.errorhandler(404)
    def _nao_encontrado(erro):
        return _responder(404, messages.PAGINA_NAO_ENCONTRADA)

    @app.errorhandler(HTTPException)
    def _http(erro):
        # 404 tem handler proprio; aqui caem 405, 400, etc.
        return _responder(erro.code or 500, messages.ERRO_INESPERADO)

    @app.errorhandler(Exception)
    def _inesperado(erro):
        logger.exception("Erro inesperado")
        return _responder(500, messages.ERRO_INESPERADO)


def _responder(status: int, mensagem: str):
    """Responde JSON nas rotas /api e pagina HTML amigavel nas demais."""
    if request.path.startswith("/api"):
        return jsonify({"erro": mensagem}), status
    return render_template("error.html", status=status, mensagem=mensagem), status
