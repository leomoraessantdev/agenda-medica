"""Testes do tratamento de falhas (Parte 2): banco indisponivel e paginas de erro."""
import pytest
from sqlalchemy.exc import SQLAlchemyError

from app.blueprints.auth import routes as auth_routes
from app.exceptions.domain import BancoIndisponivelError
from app.repositories import user_repository


def _obter_csrf(client):
    client.get("/login")
    with client.session_transaction() as sess:
        return sess.get("_csrf_token")


def test_pagina_nao_encontrada_amigavel(client):
    resp = client.get("/rota-que-nao-existe")
    assert resp.status_code == 404
    corpo = resp.get_data(as_text=True).lower()
    assert "nao encontrada" in corpo
    assert "traceback" not in corpo  # nunca vaza stack trace


def test_repositorio_traduz_erro_de_banco(app, monkeypatch):
    class _QueryQuebrada:
        def filter(self, *args, **kwargs):
            raise SQLAlchemyError("conexao perdida")

    monkeypatch.setattr(user_repository.User, "query", _QueryQuebrada())
    with pytest.raises(BancoIndisponivelError):
        user_repository.UserRepository().find_by_login("medico")


def test_login_com_banco_indisponivel(client, monkeypatch):
    def _boom(*args, **kwargs):
        raise BancoIndisponivelError()

    monkeypatch.setattr(auth_routes._auth_service, "authenticate", _boom)
    token = _obter_csrf(client)
    resp = client.post(
        "/login",
        data={"login": "medico", "senha": "qualquer", "_csrf_token": token},
    )
    assert resp.status_code == 503
    assert "indisponivel" in resp.get_data(as_text=True).lower()
