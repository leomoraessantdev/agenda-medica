"""Protecao CSRF minima baseada em token de sessao (sem dependencia extra)."""
import secrets

from flask import session


def generate_csrf_token() -> str:
    """Devolve o token da sessao, criando um na primeira chamada."""
    token = session.get("_csrf_token")
    if token is None:
        token = secrets.token_urlsafe(32)
        session["_csrf_token"] = token
    return token


def validate_csrf(token: str | None) -> bool:
    esperado = session.get("_csrf_token")
    return bool(esperado) and secrets.compare_digest(token or "", esperado)
